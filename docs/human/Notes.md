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
- Ask agent to update frontend service with `--web-root` flag and serving different index pages for different endpoints.
- Ask agent to add API tracing and logging (Claude Sonnet automatically verified the changes by testing the APIs and it fixed other issues during this process).

## Test Generation

Tests are generated in 2 steps:
1. Generate test cases in markdown files, in natural language, and this can be maintained by human;
2. Generate test spec (the test configuration or code to run the tests) according to the markdown files.
   This step also synchronizes the existing test specs from updated test cases.

By running the test specs, the reports can be used as feedback to next iteration of code generation.

The prompt used to generate test cases:

For APIs:
```
generate API test cases in markdown files according to the API definitions and the business logic.
Make sure each test case file contains:
- a short summary
- a detailed description
- test steps
- any validations needed in test steps
```

For E2E user flows:
```
generate test cases in markdown files according to the application user flows and API definitions.
Make sure each test case file contains: a short summary, a detailed description, test steps, and any validations needed in test steps.
```

The agent is not familiar with `uv`, and struggles a bit generating code with correct configuration and setup.
Manually updated the code after generation.
