import React from 'react';
import ReactDOM from 'react-dom/client';
import { ApolloProvider } from '@apollo/client';
import CustomerApp from './CustomerApp';
import { apolloClient } from '../shared/apolloClient';
import '../shared/styles.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ApolloProvider client={apolloClient}>
      <CustomerApp />
    </ApolloProvider>
  </React.StrictMode>
);
