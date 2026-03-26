# 技术设计

当一个用户第一次建立 websocket 链接时，将 websocket 链接注册到 ConnectionManager

## Actions

websocket 消息均为 json 格式，并且必须有一个 action 字段，action 的 设计如下

### HeartBeat

```json
{
  "action": "HeartBeat"
}
```

心跳包，如果长时间无响应则从 ConnectionManager 中删除链接

### JoinChatRoom

```json
{
  "action": "JoinChatRoom",
  "ChatRoomID": 1,
  "SinceMessageID": 1
}
```

一个用户同一时刻只能加入一个chat room，加入新的会自动退出上一个。

- ChatRoomID 要加入哪个 chatroom
- SinceMessageID （可选）请求返回这个 message 之后的消息。不加这个参数，默认返回最近的 1000 条

### ListMessages

```json
{
  "action": "ListMessages",
  "ChatRoomID": 1,
  "SinceMessageID": 1,
  "Before": 1
}
```

请求返回聊天内容，一次最多返回 1000 条

### ExitChatRoom

```json
{
  "action": "ExitChatRoom"
}
```

### SendMessage

```json
{
  "action": "SendMessage",
  "message": ""
}
```

用户向当前加入的群聊发送消息

### ChatMessages

```json
{
  "action": "ChatMessages",
  "messages": []
}
```

message item 的定义

```json
{
  "username": "",
  "timestamp": 0,
  "message": ""
}
```

后端向用户推送群聊内的增量新消息

### Error

```json
{
  "action": "Error",
  "message": ""
}
```

## 服务器的逻辑

以星星的 HIP 对应redis的一个 channel
当用户进入群聊时，后端 console 实例根据该用户所属的群 ID，代表用户向 Redis 订阅对应的 Channel
有人在群里发消息，console 只需要 PUBLISH group:channel:1001 "message"
