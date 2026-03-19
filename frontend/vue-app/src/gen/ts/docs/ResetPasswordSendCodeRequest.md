
# ResetPasswordSendCodeRequest


## Properties

Name | Type
------------ | -------------
`email` | string
`userName` | string

## Example

```typescript
import type { ResetPasswordSendCodeRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "email": user@example.com,
  "userName": name,
} satisfies ResetPasswordSendCodeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ResetPasswordSendCodeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


