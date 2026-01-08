# Agents Guide

## Directory Structure

- `docs`: containing the requirements and designs
  - `App.md`: the top-level product requirements
- `src`: the source code of services and shared libraries
  - `frontend`: the frontend service
  - `transaction`: the transaction service
    - `gen`: the generated protobuf/gRPC files
  - `messaging`: the messaging service
  - `apis`: the API definitions
    - `graphql`: the GraphQL definition exposed by the frontend service
    - `proto`: the Protobuf and gRPC definition of backend APIs
  - `db`: the database schema and migrations
    - `migrations`: the SQL migrations
