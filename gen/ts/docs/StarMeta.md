
# StarMeta


## Properties

Name | Type
------------ | -------------
`hIP` | number
`equatorialCoordinate` | [EquatorialCoordinate](EquatorialCoordinate.md)
`magnitude` | number
`pmRA` | number
`pmDE` | number
`bvColor` | number

## Example

```typescript
import type { StarMeta } from ''

// TODO: Update the object below with actual values
const example = {
  "hIP": null,
  "equatorialCoordinate": null,
  "magnitude": null,
  "pmRA": null,
  "pmDE": null,
  "bvColor": null,
} satisfies StarMeta

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StarMeta
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


