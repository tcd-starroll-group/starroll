
# PaginationQuery

Reusable pagination and sorting parameters for list endpoints

## Properties

Name | Type
------------ | -------------
`limit` | number
`offset` | number
`sort` | string
`order` | string

## Example

```typescript
import type { PaginationQuery } from ''

// TODO: Update the object below with actual values
const example = {
  "limit": null,
  "offset": null,
  "sort": createTime,
  "order": null,
} satisfies PaginationQuery

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PaginationQuery
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


