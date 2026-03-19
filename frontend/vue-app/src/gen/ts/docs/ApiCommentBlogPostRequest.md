
# ApiCommentBlogPostRequest


## Properties

Name | Type
------------ | -------------
`userCredentials` | [UserCredentials](UserCredentials.md)
`blogID` | string
`commentText` | string

## Example

```typescript
import type { ApiCommentBlogPostRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "userCredentials": null,
  "blogID": null,
  "commentText": null,
} satisfies ApiCommentBlogPostRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiCommentBlogPostRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


