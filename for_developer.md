# For Development

## workflow

Whenever you begin developing a new requirement:

1. API Design: You MUST first design the interfaces for your features and update the openapiv3.yaml file.

2. Technical Design: Complete the technical design for the feature. You MAY schedule a meeting to conduct a formal peer review.

3. Documentation: For complex requirements or those involving collaboration, you SHOULD write a technical design document. Link the document URL to the corresponding Jira ticket.

4. Testing: You SHOULD follow a Test-Driven Development (TDD) approach by writing unit tests before implementing the feature. You MUST include these unit tests when submitting your code.

5. Finally, you MUST open a Pull Request (PR) and adhere to the following steps: You MUST paste the Pull Request link into the corresponding Jira ticket. You MUST post both the Jira ticket link and the Pull Request link to the team group chat to request a code review. You MUST track the progress of the Pull Request, implement changes based on feedback, and ensure the code is successfully merged.

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
