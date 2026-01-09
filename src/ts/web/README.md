# API Demo Web Site

A TypeScript-based web application for an online shop with separate customer and admin interfaces.

## Overview

This web application provides:
- **Customer Interface** (`index.html`): Browse products, add to cart, and place orders
- **Admin Interface** (`admin.html`): Manage inventory and orders

Both interfaces share the same static assets but have different entry points.

## Architecture

### Customer Features
- **Landing Page**: Grid view of products with infinite scroll
- **Product Detail Page**: Modal view with product details
- **Shopping Cart**: Add/remove items and adjust quantities
- **Checkout Page**: Review cart and proceed to payment
- **Payment Page**: Enter customer information
- **Thank You Page**: Order confirmation

### Admin Features
- **Inventory Management**:
  - List all products with pagination
  - Edit product details
  - Toggle product availability
  - Remove products
- **Order Management**:
  - List all orders with pagination
  - Update order status (Ship, Complete, Cancel)

## Tech Stack

- **TypeScript**: Type-safe JavaScript
- **React**: UI framework
- **Vite**: Fast build tool with HMR (Hot Module Replacement)
- **Apollo Client**: GraphQL client for data fetching
- **GraphQL Code Generator**: Automatic type generation from GraphQL schema
- **CSS**: Component-scoped styling

## Project Structure

```
src/ts/web/
├── index.html           # Customer entry point
├── admin.html           # Admin entry point
├── codegen.ts           # GraphQL Code Generator configuration
├── src/
│   ├── customer/        # Customer-facing code
│   │   ├── pages/       # Customer page components
│   │   ├── queries.ts   # Customer GraphQL queries
│   │   ├── CustomerApp.tsx
│   │   └── index.tsx    # Customer entry point
│   ├── admin/           # Admin-facing code
│   │   ├── pages/       # Admin page components
│   │   ├── queries.ts   # Admin GraphQL queries
│   │   ├── AdminApp.tsx
│   │   └── index.tsx    # Admin entry point
│   ├── shared/          # Shared code
│   │   ├── types.ts     # TypeScript interfaces
│   │   ├── helpers.ts   # Helper functions and converters
│   │   ├── styles.css   # Global styles
│   │   └── apolloClient.ts  # Apollo Client setup
│   └── generated/       # Auto-generated GraphQL types
│       └── graphql.ts   # Generated TypeScript types
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Getting Started

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The dev server is configured to accept connections from any client (host: true), making it accessible from:
- Customer interface: http://localhost:3000/
- Admin interface: http://localhost:3000/admin.html
- Or from other devices on the network using your machine's IP address

### Production Build

Build the application:

```bash
npm run build
```

The output will be in the `dist/` directory with two entry points:
- `index.html` - Customer interface
- `admin.html` - Admin interface

Preview the production build locally:

```bash
npm run preview
```

### Type Checking

Run TypeScript type checking:

```bash
npm run type-check
```

## Implementation Details

### Dual Entry Points

The Vite multi-page app configuration creates two separate bundles:
- `main.[hash].js` loaded by `index.html` (customer interface)
- `admin.[hash].js` loaded by `admin.html` (admin interface)

Both bundles share common dependencies (React) but have separate application logic. Vite automatically handles code splitting and optimizes the shared chunks.

### GraphQL Integration

The application uses Apollo Client to fetch data from the GraphQL API at `/graphql`. The API follows the schema defined in `src/apis/graphql/`.

**Type Generation:**
- TypeScript types are automatically generated from the GraphQL schema using GraphQL Code Generator
- Run `npm run codegen` to regenerate types after schema changes
- Generated types are in `src/generated/graphql.ts`

**Data Flow:**
- Customer cart state is managed server-side via GraphQL mutations
- Product and order data are fetched from the backend
- Apollo Client cache handles data synchronization and optimistic updates

**Queries and Mutations:**
- Customer queries: `src/customer/queries.ts`
- Admin queries: `src/admin/queries.ts`
- All operations use generated TypeScript types for type safety

### Development Workflow

1. **Schema Changes**: When the GraphQL schema in `src/apis/graphql` is updated, run `npm run codegen` to regenerate types
2. **Adding Queries**: Add new queries/mutations to `src/customer/queries.ts` or `src/admin/queries.ts`, then run codegen
3. **Type Safety**: All GraphQL operations have generated TypeScript types for compile-time validation

### Future Enhancements

- Add authentication for admin interface
- Implement image upload for product management (currently uses data URIs)
- Add search and filtering capabilities
- Add real-time updates via GraphQL subscriptions
- Implement optimistic UI updates for better UX
