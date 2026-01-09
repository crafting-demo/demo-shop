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
