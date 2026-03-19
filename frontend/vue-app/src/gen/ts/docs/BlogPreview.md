
# BlogPreview

Preview of a blog on the blogs page, before user clicks into one blog

## Properties

Name | Type
------------ | -------------
`blogID` | string
`title` | string
`imageURL` | string

## Example

```typescript
import type { BlogPreview } from ''

// TODO: Update the object below with actual values
const example = {
  "blogID": null,
  "title": null,
  "imageURL": null,
} satisfies BlogPreview

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BlogPreview
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


