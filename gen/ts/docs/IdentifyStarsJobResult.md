
# IdentifyStarsJobResult

result of identify stars job

## Properties

Name | Type
------------ | -------------
`center` | [EquatorialCoordinate](EquatorialCoordinate.md)
`identifiedStars` | [Array&lt;IdentifyStarsJobResultIdentifiedStarsInner&gt;](IdentifyStarsJobResultIdentifiedStarsInner.md)
`oriImageUrl` | string

## Example

```typescript
import type { IdentifyStarsJobResult } from ''

// TODO: Update the object below with actual values
const example = {
  "center": null,
  "identifiedStars": null,
  "oriImageUrl": null,
} satisfies IdentifyStarsJobResult

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as IdentifyStarsJobResult
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


