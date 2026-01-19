
# ErrorResponse

General error response

## Properties

Name | Type
------------ | -------------
`code` | string
`message` | string

## Example

```typescript
import type { ErrorResponse } from ''

// TODO: Update the object below with actual values
const example = {
  "code": AUTH_001,
  "message": Invalid username or password,
} satisfies ErrorResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ErrorResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


