
# CommentItem


## Properties

Name | Type
------------ | -------------
`commentID` | string
`commentText` | string
`userID` | string
`time` | string

## Example

```typescript
import type { CommentItem } from ''

// TODO: Update the object below with actual values
const example = {
  "commentID": null,
  "commentText": null,
  "userID": null,
  "time": null,
} satisfies CommentItem

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CommentItem
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


