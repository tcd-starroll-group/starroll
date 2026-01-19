
# ApiElimilateErrorsPostRequest


## Properties

Name | Type
------------ | -------------
`cameraMeta` | [CameraMeta](CameraMeta.md)
`image` | string
`starCoordinates` | [Array&lt;ApiCalculateStarCoordinatesPost200ResponseStarCoordinatesInner&gt;](ApiCalculateStarCoordinatesPost200ResponseStarCoordinatesInner.md)

## Example

```typescript
import type { ApiElimilateErrorsPostRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "cameraMeta": null,
  "image": null,
  "starCoordinates": null,
} satisfies ApiElimilateErrorsPostRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiElimilateErrorsPostRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


