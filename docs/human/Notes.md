# Vibe Notes

## Procedure

- Spec product design in [App.md](../App.md);
- Breakdown architecture into individual markdown files for each service;
- Spec web site coding guide;
- Create [AGENTS.md](../../AGENTS.md) as the top level index and describe directory layout.
- Ask agent to generate GraphQL schemas;
- Ask agent to generate gRPC APIs;
- Ask agent to generate initial database schema and migrations;
- Ask agent to generate frontend and transaction services as they share the same Go project tree
  - Manual editing is required as it's challenging for agent to correctly generate code from GraphQL schema
    which is separated for customer facing APIs and admin facing APIs;
- Ask agent to generate website, and must explicitly mention
  - Use `vite` rather than `webpack`;
  - Use GraphQL APIs rather than mock data;
  - Directly use data types generated from GraphQL schema rather than redefine with convertion logic.
