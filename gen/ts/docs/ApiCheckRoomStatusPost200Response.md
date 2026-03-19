
# ApiCheckRoomStatusPost200Response


## Properties

Name | Type
------------ | -------------
`message` | string
`roomID` | string
`isJoinable` | boolean
`status` | string

## Example

```typescript
import type { ApiCheckRoomStatusPost200Response } from ''

// TODO: Update the object below with actual values
const example = {
  "message": Operation successful,
  "roomID": null,
  "isJoinable": null,
  "status": null,
} satisfies ApiCheckRoomStatusPost200Response

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiCheckRoomStatusPost200Response
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


