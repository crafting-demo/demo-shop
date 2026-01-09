# Frontend Service

This service exposes 2 listeners.
Both serving GraphQL APIs, one for customer user flows and the other for admin user flows.
It also serves the full website on both listeners.

## External API

The GraphQL APIs are exposed externally.
The implementation will use gRPC API to talk to the backend services:
- [Transaction Service](TransactionService.md): for actual data model manipulations.
