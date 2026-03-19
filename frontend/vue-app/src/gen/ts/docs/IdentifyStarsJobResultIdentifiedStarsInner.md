
# IdentifyStarsJobResultIdentifiedStarsInner


## Properties

Name | Type
------------ | -------------
`names` | Array&lt;string&gt;
`pixelX` | number
`pixelY` | number
`vmag` | number
`hIP` | number

## Example

```typescript
import type { IdentifyStarsJobResultIdentifiedStarsInner } from ''

// TODO: Update the object below with actual values
const example = {
  "names": ["108Vir"],
  "pixelX": 1676.0093296680352,
  "pixelY": 629.9991687682354,
  "vmag": 5.6,
  "hIP": null,
} satisfies IdentifyStarsJobResultIdentifiedStarsInner

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as IdentifyStarsJobResultIdentifiedStarsInner
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


