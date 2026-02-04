
# ApiUserRegPostRequest


## Properties

Name | Type
------------ | -------------
`username` | string
`password` | string
`email` | string

## Example

```typescript
import type { ApiUserRegPostRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "username": user123,
  "password": Str0ngPa$$w0rd!,
  "email": user@example.com,
} satisfies ApiUserRegPostRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiUserRegPostRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


