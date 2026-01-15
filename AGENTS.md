# Agents Guide

## Directory Structure

- `docs`: containing the requirements and designs
  - `App.md`: the top-level product requirements
- `src`: the source code of services and shared libraries
  - `go`: all Go source code
    - `cmd/transd`: the main package of transaction service
    - `cmd/frontd`: the main package of frontend service
    - `gen`: the generated code
    - `pkg`: shared packages
      - `transaction`: the transaction service
      - `frontend`: the frontend service
  - `ts`: all TypeScript source code
    - `web`: the [WebSite](#docs/WebSite.md)
  - `apis`: the API definitions
    - `graphql`: the GraphQL definition exposed by the frontend service
    - `proto`: the Protobuf and gRPC definition of backend APIs
  - `db`: the database schema and migrations
    - `migrations`: the SQL migrations
    - `examples`: the SQL script creating example products if they don't exist
- `test`: the test case docs and test spec and code
  - `docs`: all the test cases in markdown
    - `api`: the test cases specially for testing the APIs
    - `e2e`: the test cases covering the E2E user flows
  - `spec`: the test specs according to the test cases in `docs` folder
    - `api`: the test code in Python corresponding to the API cases, test report in `test-results.xml`

## Build All

This source tree contains all generated code, and can be build directly:

```shell
./scripts/build-all.sh
```

To regenerate code:

```shell
./scripts/generate.sh
```
