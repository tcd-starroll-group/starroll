
# ApiTriggerStarfieldRenderPostRequest


## Properties

Name | Type
------------ | -------------
`cameraMeta` | [CameraMeta](CameraMeta.md)
`correctedStarCoordinates` | [Array&lt;ApiTriggerStarfieldRenderPostRequestCorrectedStarCoordinatesInner&gt;](ApiTriggerStarfieldRenderPostRequestCorrectedStarCoordinatesInner.md)
`renderParams` | [ApiTriggerStarfieldRenderPostRequestRenderParams](ApiTriggerStarfieldRenderPostRequestRenderParams.md)

## Example

```typescript
import type { ApiTriggerStarfieldRenderPostRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "cameraMeta": null,
  "correctedStarCoordinates": null,
  "renderParams": null,
} satisfies ApiTriggerStarfieldRenderPostRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApiTriggerStarfieldRenderPostRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


