import React from 'react';
import ReactDOM from 'react-dom/client';
import { ApolloProvider } from '@apollo/client';
import AdminApp from './AdminApp';
import { apolloClient } from '../shared/apolloClient';
import '../shared/styles.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ApolloProvider client={apolloClient}>
      <AdminApp />
    </ApolloProvider>
  </React.StrictMode>
);
