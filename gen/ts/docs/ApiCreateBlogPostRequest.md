
# ApiCreateBlogPostRequest


## Properties

Name | Type
------------ | -------------
`userCredentials` | [UserCredentials](UserCredentials.md)
`hIP` | string
`title` | string
`imageURLList` | Array&lt;string&gt;
`content` | string

## Example

```typescript
import type { ApiCreateBlogPostRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "userCredentials": null,
  "hIP": null,
  "title": null,
  "imageURLList": null,
  "content": null,
} satisfies ApiCreateBlogPostRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiCreateBlogPostRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


