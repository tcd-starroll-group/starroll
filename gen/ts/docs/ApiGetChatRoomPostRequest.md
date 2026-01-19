
# ApiGetChatRoomPostRequest


## Properties

Name | Type
------------ | -------------
`roomId` | string
`userId` | string
`userStatus` | boolean
`roomStatus` | boolean

## Example

```typescript
import type { ApiGetChatRoomPostRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "roomId": null,
  "userId": null,
  "userStatus": null,
  "roomStatus": null,
} satisfies ApiGetChatRoomPostRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiGetChatRoomPostRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


