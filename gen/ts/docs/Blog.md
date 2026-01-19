
# Blog

Details of one blog

## Properties

Name | Type
------------ | -------------
`blogID` | string
`title` | string
`imageURLList` | Array&lt;string&gt;
`content` | string
`commentList` | [Array&lt;CommentItem&gt;](CommentItem.md)
`commentNumber` | number
`likeNumber` | number

## Example

```typescript
import type { Blog } from ''

// TODO: Update the object below with actual values
const example = {
  "blogID": null,
  "title": null,
  "imageURLList": null,
  "content": null,
  "commentList": null,
  "commentNumber": null,
  "likeNumber": null,
} satisfies Blog

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as Blog
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


