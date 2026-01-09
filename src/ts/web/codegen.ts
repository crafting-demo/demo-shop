import type { CodegenConfig } from '@graphql-codegen/cli';

const config: CodegenConfig = {
  overwrite: true,
  schema: [
    '../../apis/graphql/types.graphql',
    '../../apis/graphql/customer.graphql',
    '../../apis/graphql/admin.graphql',
  ],
  documents: ['src/**/*.tsx', 'src/**/*.ts', '!src/generated/**/*'],
  ignoreNoDocuments: true,
  generates: {
    'src/generated/graphql.ts': {
      plugins: [
        'typescript',
        'typescript-operations',
        'typescript-react-apollo',
      ],
      config: {
        withHooks: true,
        skipTypename: false,
        enumsAsTypes: true,
        scalars: {
          Time: 'string',
        },
      },
    },
  },
};

export default config;
