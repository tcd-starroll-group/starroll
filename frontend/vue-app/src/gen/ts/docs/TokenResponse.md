
# TokenResponse

The access token returned after successful login

## Properties

Name | Type
------------ | -------------
`token` | string
`expiresIn` | number
`userID` | string

## Example

```typescript
import type { TokenResponse } from ''

// TODO: Update the object below with actual values
const example = {
  "token": eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...,
  "expiresIn": 3600,
  "userID": 1,
} satisfies TokenResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TokenResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


