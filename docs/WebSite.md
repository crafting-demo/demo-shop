# Web Site

## Assets

The Web Site contains a single copy of static assets for both
Customer facing endpoint and Admin facing endpoint.
The implementation generates 2 different index HTML files:
- `index.html` for Customer facing endpoint;
- `admin.html` for Admin facing endpoint.

The rest of static assets can be shared by both endpoints.

## API

Use `/graphql` path to call GraphQL APIs for manipulating data models which
is generated from the GraphQL schema and should be directly used in code.
