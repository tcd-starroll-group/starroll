
# ProfileStatsResponse


## Properties

Name | Type
------------ | -------------
`starsDiscovered` | number
`totalScans` | number
`rank` | string
`joinDate` | string

## Example

```typescript
import type { ProfileStatsResponse } from ''

// TODO: Update the object below with actual values
const example = {
  "starsDiscovered": null,
  "totalScans": null,
  "rank": null,
  "joinDate": null,
} satisfies ProfileStatsResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ProfileStatsResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


