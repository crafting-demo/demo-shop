import React from 'react';
import ReactDOM from 'react-dom/client';
import { ApolloProvider } from '@apollo/client';
import CustomerApp from './CustomerApp';
import { apolloClient } from '../shared/apolloClient';
import { ThemeProvider } from '../shared/ThemeContext';
import '../shared/styles.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ThemeProvider>
      <ApolloProvider client={apolloClient}>
        <CustomerApp />
      </ApolloProvider>
    </ThemeProvider>
  </React.StrictMode>
);
