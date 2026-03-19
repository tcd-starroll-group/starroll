
# ApiGetChatRoomInfoPost200Response


## Properties

Name | Type
------------ | -------------
`roomID` | string
`name` | string
`description` | string
`creationTime` | string
`onlineUsers` | number
`members` | [Array&lt;ApiGetChatRoomInfoPost200ResponseMembersInner&gt;](ApiGetChatRoomInfoPost200ResponseMembersInner.md)

## Example

```typescript
import type { ApiGetChatRoomInfoPost200Response } from ''

// TODO: Update the object below with actual values
const example = {
  "roomID": null,
  "name": null,
  "description": null,
  "creationTime": null,
  "onlineUsers": null,
  "members": null,
} satisfies ApiGetChatRoomInfoPost200Response

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiGetChatRoomInfoPost200Response
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


