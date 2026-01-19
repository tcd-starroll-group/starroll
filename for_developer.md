# For Development

## Vue

```bash
cd vue-app
npm install
npm run format
npm run dev
```

## Generate Code from IDL

### Generate Python Code

```bash
docker run --rm \
    -v "${PWD}:/local" \
    openapitools/openapi-generator-cli generate \
    -i /local/idl/openapiv3.yaml \
    -g python-fastapi \
    -o /local/gen/py
```

### Generate TypeScript Code

```bash
docker run --rm \
 -v "${PWD}:/local" \
 openapitools/openapi-generator-cli generate \
 -i /local/idl/openapiv3.yaml \
 -g typescript-fetch \
 -o /local/gen/ts
```

## Unit Testing

For TypeScript unit testing, refer to frontend/vue-app/src/utils/astronomy.test.ts
Run unit tests:

```bash
npm run test:unit
```
