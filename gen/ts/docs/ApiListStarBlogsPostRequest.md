
# ApiListStarBlogsPostRequest


## Properties

Name | Type
------------ | -------------
`limit` | number
`offset` | number
`sort` | string
`order` | string
`hIP` | string

## Example

```typescript
import type { ApiListStarBlogsPostRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "limit": null,
  "offset": null,
  "sort": createTime,
  "order": null,
  "hIP": null,
} satisfies ApiListStarBlogsPostRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiListStarBlogsPostRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


