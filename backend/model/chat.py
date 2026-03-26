from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HeartBeatAction(BaseModel):
    action: Literal["HeartBeat"]


class JoinChatRoomAction(BaseModel):
    action: Literal["JoinChatRoom"]
    ChatRoomID: int
    SinceMessageID: int | None = None


class ListMessagesAction(BaseModel):
    action: Literal["ListMessages"]
    ChatRoomID: int
    SinceMessageID: int | None = None
    Before: int | None = None


class ExitChatRoomAction(BaseModel):
    action: Literal["ExitChatRoom"]


class SendMessageAction(BaseModel):
    action: Literal["SendMessage"]
    message: str


class ChatMessageItem(BaseModel):
    username: str
    timestamp: int
    message: str
    message_id: int | None = None


class ChatMessagesAction(BaseModel):
    action: Literal["ChatMessages"]
    messages: list[ChatMessageItem]


class ErrorAction(BaseModel):
    action: Literal["Error"]
    message: str


class ChatMessageKafkaEvent(BaseModel):
    user_id: int | str
    chatroom_id: int | str
    message_id: int
    message: str


ClientToServerAction = (
    HeartBeatAction
    | JoinChatRoomAction
    | ListMessagesAction
    | ExitChatRoomAction
    | SendMessageAction
)

ServerToClientAction = ChatMessagesAction | ErrorAction

AnyChatAction = ClientToServerAction | ServerToClientAction
