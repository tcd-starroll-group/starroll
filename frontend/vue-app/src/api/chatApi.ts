// ---------------------------------------------------------------------------
// Chat WebSocket Client
// ---------------------------------------------------------------------------

// ── Client → Server actions ─────────────────────────────────────────────────

export interface HeartBeatAction {
  action: 'HeartBeat'
}

export interface JoinChatRoomAction {
  action: 'JoinChatRoom'
  /** ID of the chat room to join */
  ChatRoomID: number
  /** When provided, only messages after this ID are returned on join */
  SinceMessageID?: number
}

export interface ListMessagesAction {
  action: 'ListMessages'
  ChatRoomID: number
  /** Return messages newer than this ID */
  SinceMessageID?: number
  /** Return messages older than this ID (pagination) */
  AfterMessageID?: number
}

export interface ExitChatRoomAction {
  action: 'ExitChatRoom'
}

export interface SendMessageAction {
  action: 'SendMessage'
  message: string
}

export type ClientToServerAction =
  | HeartBeatAction
  | JoinChatRoomAction
  | ListMessagesAction
  | ExitChatRoomAction
  | SendMessageAction

// ── Server → Client actions ──────────────────────────────────────────────────

export interface ChatMessageItem {
  username: string
  /** Unix timestamp (seconds) */
  timestamp: number
  message: string
  message_id?: number
}

export interface ChatMessagesAction {
  action: 'ChatMessages'
  messages: ChatMessageItem[]
}

export interface ErrorAction {
  action: 'Error'
  message: string
}

export type ServerToClientAction = ChatMessagesAction | ErrorAction

// ── Event callbacks ──────────────────────────────────────────────────────────

export interface ChatClientCallbacks {
  /** Fired when the WebSocket connection is established */
  onConnect?: () => void
  /** Fired when the connection is closed (intentionally or by error) */
  onDisconnect?: (code: number, reason: string) => void
  /** Fired when the server pushes new chat messages */
  onMessages?: (messages: ChatMessageItem[]) => void
  /** Fired when the server sends an error action */
  onError?: (message: string) => void
}

// ── Constants ────────────────────────────────────────────────────────────────

/** Interval between heartbeat pings sent to the server (ms) */
const HEARTBEAT_INTERVAL_MS = 10_000

/** Base delay before a reconnect attempt (ms) */
const RECONNECT_BASE_DELAY_MS = 2_000

/** Maximum delay between reconnect attempts (ms) */
const RECONNECT_MAX_DELAY_MS = 30_000

/** Maximum number of consecutive reconnect attempts (0 = unlimited) */
const RECONNECT_MAX_ATTEMPTS = 0

// ── ChatWebSocketClient ───────────────────────────────────────────────────────

export class ChatWebSocketClient {
  private ws: WebSocket | null = null
  private callbacks: ChatClientCallbacks = {}
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private reconnectAttempts = 0
  private intentionalClose = false

  /**
   * URL of the WebSocket endpoint, e.g. `ws://localhost:8000/api/chat`.
   * The `token` query-parameter is appended automatically on connect.
   */
  private readonly baseUrl: string

  constructor(baseUrl?: string) {
    // Derive the WS base URL from the current page origin when not provided
    const origin = typeof window !== 'undefined' ? window.location.origin : ''
    const wsOrigin = origin.replace(/^http/, 'ws')
    this.baseUrl = baseUrl ?? `${wsOrigin}/api/chat`
  }

  // ── Public API ─────────────────────────────────────────────────────────────

  /** Register event callbacks. Can be called multiple times to update handlers. */
  setCallbacks(callbacks: ChatClientCallbacks): void {
    this.callbacks = { ...this.callbacks, ...callbacks }
  }

  /**
   * Open the WebSocket connection.
   * @param token  JWT access token read from localStorage (or passed explicitly)
   */
  connect(token?: string): void {
    if (this.ws && this.isOpen()) {
      return
    }
    this.intentionalClose = false
    this._openSocket(token ?? localStorage.getItem('token') ?? '')
  }

  /** Close the connection and stop reconnection attempts. */
  disconnect(): void {
    this.intentionalClose = true
    this._stopHeartbeat()
    this._cancelReconnect()
    if (this.ws) {
      this.ws.close(1000, 'client disconnect')
      this.ws = null
    }
  }

  /** Whether the underlying WebSocket is currently open. */
  isOpen(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  // ── Chat actions ──────────────────────────────────────────────────────────

  /**
   * Join a chat room.  The server will immediately send back up to 1000
   * recent messages (or messages after `sinceMessageId` when specified).
   */
  joinRoom(roomId: number, sinceMessageId?: number): void {
    const action: JoinChatRoomAction = {
      action: 'JoinChatRoom',
      ChatRoomID: roomId,
      ...(sinceMessageId !== undefined && { SinceMessageID: sinceMessageId }),
    }
    this._send(action)
  }

  /** Leave the currently joined chat room. */
  exitRoom(): void {
    this._send({ action: 'ExitChatRoom' })
  }

  /**
   * Request a list of messages.
   * - `sinceMessageId`: return messages newer than this ID
   * - `afterMessageId`: return messages older than this ID (pagination)
   */
  listMessages(
    roomId: number,
    options: { sinceMessageId?: number; afterMessageId?: number } = {},
  ): void {
    const action: ListMessagesAction = {
      action: 'ListMessages',
      ChatRoomID: roomId,
      ...(options.sinceMessageId !== undefined && {
        SinceMessageID: options.sinceMessageId,
      }),
      ...(options.afterMessageId !== undefined && {
        AfterMessageID: options.afterMessageId,
      }),
    }
    this._send(action)
  }

  /** Send a chat message to the room the user is currently in. */
  sendMessage(message: string): void {
    if (!message.trim()) return
    this._send({ action: 'SendMessage', message })
  }

  // ── Internal helpers ──────────────────────────────────────────────────────

  private _openSocket(token: string): void {
    const url = token ? `${this.baseUrl}?token=${encodeURIComponent(token)}` : this.baseUrl

    const ws = new WebSocket(url)
    this.ws = ws

    ws.onopen = () => {
      this.reconnectAttempts = 0
      this._startHeartbeat()
      this.callbacks.onConnect?.()
    }

    ws.onmessage = (event: MessageEvent) => {
      this._handleMessage(event.data as string)
    }

    ws.onerror = () => {
      // onerror is always followed by onclose; handle cleanup there
    }

    ws.onclose = (event: CloseEvent) => {
      this._stopHeartbeat()
      this.ws = null
      this.callbacks.onDisconnect?.(event.code, event.reason)

      if (!this.intentionalClose) {
        this._scheduleReconnect(token)
      }
    }
  }

  private _handleMessage(data: string): void {
    let parsed: ServerToClientAction
    try {
      parsed = JSON.parse(data) as ServerToClientAction
    } catch {
      console.warn('[ChatWebSocketClient] Received non-JSON message:', data)
      return
    }

    switch (parsed.action) {
      case 'ChatMessages':
        this.callbacks.onMessages?.(parsed.messages)
        break
      case 'Error':
        console.warn('[ChatWebSocketClient] Server error:', parsed.message)
        this.callbacks.onError?.(parsed.message)
        break
      default:
        console.warn('[ChatWebSocketClient] Unknown action:', (parsed as { action: string }).action)
    }
  }

  private _send(action: ClientToServerAction): void {
    if (!this.isOpen()) {
      console.warn('[ChatWebSocketClient] Cannot send – socket is not open')
      return
    }
    this.ws!.send(JSON.stringify(action))
  }

  private _startHeartbeat(): void {
    this._stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      this._send({ action: 'HeartBeat' })
    }, HEARTBEAT_INTERVAL_MS)
  }

  private _stopHeartbeat(): void {
    if (this.heartbeatTimer !== null) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private _scheduleReconnect(token: string): void {
    if (RECONNECT_MAX_ATTEMPTS > 0 && this.reconnectAttempts >= RECONNECT_MAX_ATTEMPTS) {
      console.warn('[ChatWebSocketClient] Max reconnect attempts reached; giving up.')
      return
    }

    const delay = Math.min(
      RECONNECT_BASE_DELAY_MS * 2 ** this.reconnectAttempts,
      RECONNECT_MAX_DELAY_MS,
    )
    this.reconnectAttempts++
    console.info(
      `[ChatWebSocketClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})…`,
    )

    this.reconnectTimer = setTimeout(() => {
      if (!this.intentionalClose) {
        this._openSocket(token)
      }
    }, delay)
  }

  private _cancelReconnect(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
}

// ── Singleton ─────────────────────────────────────────────────────────────────

/** A shared client instance.  Components should call `setCallbacks` to
 *  subscribe and `connect` / `disconnect` as needed. */
export const chatClient = new ChatWebSocketClient()
