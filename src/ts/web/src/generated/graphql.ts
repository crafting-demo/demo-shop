import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  /** A date-time string in ISO 8601 format */
  Time: { input: string; output: string; }
};

/** Input for adding a product to cart */
export type AddToCartInput = {
  /** ID of the product to add */
  productId: Scalars['ID']['input'];
  /** Number of units to add (default: 1) */
  quantity?: InputMaybe<Scalars['Int']['input']>;
};

/** Represents the shopping cart */
export type Cart = {
  __typename?: 'Cart';
  /** Unique identifier for the cart. It's immutable once created */
  id: Scalars['ID']['output'];
  /** List of items in the cart */
  items: Array<CartItem>;
  /** Total price of all items in the cart. This may be different from the sum of all items as discounts and other promotions may apply */
  totalPrice: Scalars['Int']['output'];
};

/** Represents an item in the shopping cart */
export type CartItem = {
  __typename?: 'CartItem';
  /** The product snapshot in the cart */
  product: Product;
  /** Number of units of this product in the cart */
  quantity: Scalars['Int']['output'];
  /** Total price for this cart item (pricePerUnit * quantity) */
  totalPrice: Scalars['Int']['output'];
};

/** Input for creating a new product (Admin) */
export type CreateProductInput = {
  /** Number of units in stock */
  countInStock: Scalars['Int']['input'];
  /** Detailed description of the product */
  description?: InputMaybe<Scalars['String']['input']>;
  /** Image data for the product. The value follows the data URI scheme (e.g., 'data:image/png;base64,...') */
  imageData?: InputMaybe<Scalars['String']['input']>;
  /** Display name of the product */
  name: Scalars['String']['input'];
  /** Price per unit in cents */
  pricePerUnit: Scalars['Int']['input'];
  /** Initial availability state (default: AVAILABLE) */
  state?: InputMaybe<ProductState>;
};

export type Mutation = {
  __typename?: 'Mutation';
  /** Add a product to the shopping cart */
  addToCart: Cart;
  /**
   * Cancel an order.
   * Only available when current state is PROCESSING or SHIPPED.
   */
  cancelOrder: Order;
  /** Clear all items from the cart */
  clearCart: Cart;
  /**
   * Mark an order as completed.
   * Only available when current state is SHIPPED.
   */
  completeOrder: Order;
  /** Create a new product in the inventory */
  createProduct: Product;
  /**
   * Place an order with the items in the cart.
   * This will create an order and clear the cart.
   */
  placeOrder: Order;
  /** Set a product's state to AVAILABLE */
  putProductOnShelf: Product;
  /** Remove a product from the cart */
  removeFromCart: Cart;
  /** Remove a product from the inventory (soft delete) */
  removeProduct: Scalars['Boolean']['output'];
  /**
   * Mark an order as shipped.
   * Only available when current state is PROCESSING.
   */
  shipOrder: Order;
  /** Set a product's state to OFF_SHELF */
  takeProductOffShelf: Product;
  /** Update the quantity of a product in the cart */
  updateCartItem: Cart;
  /** Update an existing product */
  updateProduct: Product;
};


export type MutationAddToCartArgs = {
  input: AddToCartInput;
};


export type MutationCancelOrderArgs = {
  id: Scalars['ID']['input'];
};


export type MutationCompleteOrderArgs = {
  id: Scalars['ID']['input'];
};


export type MutationCreateProductArgs = {
  input: CreateProductInput;
};


export type MutationPlaceOrderArgs = {
  input: PlaceOrderInput;
};


export type MutationPutProductOnShelfArgs = {
  id: Scalars['ID']['input'];
};


export type MutationRemoveFromCartArgs = {
  productId: Scalars['ID']['input'];
};


export type MutationRemoveProductArgs = {
  id: Scalars['ID']['input'];
};


export type MutationShipOrderArgs = {
  id: Scalars['ID']['input'];
};


export type MutationTakeProductOffShelfArgs = {
  id: Scalars['ID']['input'];
};


export type MutationUpdateCartItemArgs = {
  input: UpdateCartItemInput;
};


export type MutationUpdateProductArgs = {
  input: UpdateProductInput;
};

/** Represents a customer order */
export type Order = {
  __typename?: 'Order';
  /** Timestamp when the order was placed */
  createdAt: Scalars['Time']['output'];
  /** Customer's email address */
  customerEmail: Scalars['String']['output'];
  /** Customer's name */
  customerName: Scalars['String']['output'];
  /** Unique identifier for the order */
  id: Scalars['ID']['output'];
  /** List of items in the order */
  items: Array<OrderItem>;
  /** Shipping address */
  shippingAddress: Scalars['String']['output'];
  /** Current state of the order */
  state: OrderState;
  /** Total price of the order */
  totalPrice: Scalars['Int']['output'];
  /** Timestamp when the order was last updated */
  updatedAt: Scalars['Time']['output'];
};

/** A paginated list of orders */
export type OrderConnection = {
  __typename?: 'OrderConnection';
  /** List of orders in this page */
  edges: Array<OrderEdge>;
  /** Pagination information */
  pageInfo: PageInfo;
};

/** An edge in the order connection */
export type OrderEdge = {
  __typename?: 'OrderEdge';
  /** Cursor for this order */
  cursor: Scalars['String']['output'];
  /** The order */
  node: Order;
};

/** Filter options for orders (Admin) */
export type OrderFilterInput = {
  /** Filter by customer email */
  customerEmail?: InputMaybe<Scalars['String']['input']>;
  /** Filter by order state */
  state?: InputMaybe<OrderState>;
};

/** Represents an item in an order */
export type OrderItem = {
  __typename?: 'OrderItem';
  /** The product snapshot that was ordered */
  product: Product;
  /** Number of units ordered */
  quantity: Scalars['Int']['output'];
  /** Total price for this order item */
  totalPrice: Scalars['Int']['output'];
};

/**
 * State representing order lifecycle
 * The valid state transitions are:
 * - PROCESSING -> SHIPPED (when order is dispatched)
 * - PROCESSING -> CANCELED (when order is canceled before shipping)
 * - SHIPPED -> COMPLETED (when order is delivered)
 * - SHIPPED -> CANCELED (when order is canceled after shipping)
 */
export type OrderState =
  /** Order has been canceled */
  | 'CANCELED'
  /** Order has been delivered and completed */
  | 'COMPLETED'
  /** Order has been placed and is being processed */
  | 'PROCESSING'
  /** Order has been shipped */
  | 'SHIPPED';

/** Information about pagination in a connection */
export type PageInfo = {
  __typename?: 'PageInfo';
  /** Cursor to the last item in this page */
  endCursor?: Maybe<Scalars['String']['output']>;
  /** Whether there are more items after this page */
  hasNextPage: Scalars['Boolean']['output'];
  /** Whether there are more items before this page */
  hasPreviousPage: Scalars['Boolean']['output'];
  /** Cursor to the first item in this page */
  startCursor?: Maybe<Scalars['String']['output']>;
  /** Total number of items across all pages */
  totalCount: Scalars['Int']['output'];
};

/** Input for placing an order */
export type PlaceOrderInput = {
  /** Customer's email address */
  customerEmail: Scalars['String']['input'];
  /** Customer's name */
  customerName: Scalars['String']['input'];
  /** Shipping address */
  shippingAddress: Scalars['String']['input'];
};

/** Represents a product in the shop */
export type Product = {
  __typename?: 'Product';
  /** Number of units currently in stock */
  countInStock: Scalars['Int']['output'];
  /** Timestamp when the product was created */
  createdAt: Scalars['Time']['output'];
  /** Detailed description of the product */
  description?: Maybe<Scalars['String']['output']>;
  /** Unique identifier for the product */
  id: Scalars['ID']['output'];
  /** Image data for the product. The value follows the data URI scheme (e.g., 'data:image/png;base64,...') */
  imageData?: Maybe<Scalars['String']['output']>;
  /** Display name of the product */
  name: Scalars['String']['output'];
  /** Price per unit in cents */
  pricePerUnit: Scalars['Int']['output'];
  /** Current availability state */
  state: ProductState;
  /** Timestamp when the product was last updated */
  updatedAt: Scalars['Time']['output'];
};

/** A paginated list of products */
export type ProductConnection = {
  __typename?: 'ProductConnection';
  /** List of products in this page */
  edges: Array<ProductEdge>;
  /** Pagination information */
  pageInfo: PageInfo;
};

/** An edge in the product connection */
export type ProductEdge = {
  __typename?: 'ProductEdge';
  /** Cursor for this product */
  cursor: Scalars['String']['output'];
  /** The product */
  node: Product;
};

/** Filter options for products (Admin) */
export type ProductFilterInput = {
  /** Search by name (case-insensitive partial match) */
  searchName?: InputMaybe<Scalars['String']['input']>;
  /** Filter by product state */
  state?: InputMaybe<ProductState>;
};

/** State representing product availability for customers */
export type ProductState =
  /** Product is available for purchase */
  | 'AVAILABLE'
  /** Product is currently off shelf and not available */
  | 'OFF_SHELF';

export type Query = {
  __typename?: 'Query';
  /** Get the current shopping cart for the session */
  cart: Cart;
  /** Get detailed information about a specific order */
  order?: Maybe<Order>;
  /** Get a paginated list of all orders */
  orders: OrderConnection;
  /** Get detailed information about a specific product */
  product?: Maybe<Product>;
  /**
   * Get a paginated list of available products for the shop landing page.
   * Only returns products with state AVAILABLE and countInStock > 0.
   */
  products: ProductConnection;
};


export type QueryOrderArgs = {
  id: Scalars['ID']['input'];
};


export type QueryOrdersArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  filter?: InputMaybe<OrderFilterInput>;
  first?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryProductArgs = {
  id: Scalars['ID']['input'];
};


export type QueryProductsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  filter?: InputMaybe<ProductFilterInput>;
  first?: InputMaybe<Scalars['Int']['input']>;
};

/** Input for updating cart item quantity */
export type UpdateCartItemInput = {
  /** ID of the product to update */
  productId: Scalars['ID']['input'];
  /** New quantity (0 removes the item) */
  quantity: Scalars['Int']['input'];
};

/** Input for updating an existing product (Admin) */
export type UpdateProductInput = {
  /** New count in stock */
  countInStock?: InputMaybe<Scalars['Int']['input']>;
  /** New description */
  description?: InputMaybe<Scalars['String']['input']>;
  /** ID of the product to update */
  id: Scalars['ID']['input'];
  /** New image data for the product. The value follows the data URI scheme (e.g., 'data:image/png;base64,...') */
  imageData?: InputMaybe<Scalars['String']['input']>;
  /** New display name */
  name?: InputMaybe<Scalars['String']['input']>;
  /** New price per unit in cents */
  pricePerUnit?: InputMaybe<Scalars['Int']['input']>;
  /** New availability state */
  state?: InputMaybe<ProductState>;
};

export type GetProductsAdminQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  filter?: InputMaybe<ProductFilterInput>;
}>;


export type GetProductsAdminQuery = { __typename?: 'Query', products: { __typename?: 'ProductConnection', edges: Array<{ __typename?: 'ProductEdge', cursor: string, node: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } }>, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor?: string | null, endCursor?: string | null, totalCount: number } } };

export type GetProductAdminQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetProductAdminQuery = { __typename?: 'Query', product?: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } | null };

export type GetOrdersQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  filter?: InputMaybe<OrderFilterInput>;
}>;


export type GetOrdersQuery = { __typename?: 'Query', orders: { __typename?: 'OrderConnection', edges: Array<{ __typename?: 'OrderEdge', cursor: string, node: { __typename?: 'Order', id: string, customerName: string, customerEmail: string, shippingAddress: string, totalPrice: number, state: OrderState, createdAt: string, updatedAt: string, items: Array<{ __typename?: 'OrderItem', quantity: number, totalPrice: number, product: { __typename?: 'Product', id: string, name: string, pricePerUnit: number } }> } }>, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor?: string | null, endCursor?: string | null, totalCount: number } } };

export type GetOrderQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetOrderQuery = { __typename?: 'Query', order?: { __typename?: 'Order', id: string, customerName: string, customerEmail: string, shippingAddress: string, totalPrice: number, state: OrderState, createdAt: string, updatedAt: string, items: Array<{ __typename?: 'OrderItem', quantity: number, totalPrice: number, product: { __typename?: 'Product', id: string, name: string, pricePerUnit: number } }> } | null };

export type CreateProductMutationVariables = Exact<{
  input: CreateProductInput;
}>;


export type CreateProductMutation = { __typename?: 'Mutation', createProduct: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } };

export type UpdateProductMutationVariables = Exact<{
  input: UpdateProductInput;
}>;


export type UpdateProductMutation = { __typename?: 'Mutation', updateProduct: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } };

export type PutProductOnShelfMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type PutProductOnShelfMutation = { __typename?: 'Mutation', putProductOnShelf: { __typename?: 'Product', id: string, state: ProductState } };

export type TakeProductOffShelfMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type TakeProductOffShelfMutation = { __typename?: 'Mutation', takeProductOffShelf: { __typename?: 'Product', id: string, state: ProductState } };

export type RemoveProductMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type RemoveProductMutation = { __typename?: 'Mutation', removeProduct: boolean };

export type ShipOrderMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type ShipOrderMutation = { __typename?: 'Mutation', shipOrder: { __typename?: 'Order', id: string, state: OrderState, updatedAt: string } };

export type CompleteOrderMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type CompleteOrderMutation = { __typename?: 'Mutation', completeOrder: { __typename?: 'Order', id: string, state: OrderState, updatedAt: string } };

export type CancelOrderMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type CancelOrderMutation = { __typename?: 'Mutation', cancelOrder: { __typename?: 'Order', id: string, state: OrderState, updatedAt: string } };

export type GetProductsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetProductsQuery = { __typename?: 'Query', products: { __typename?: 'ProductConnection', edges: Array<{ __typename?: 'ProductEdge', cursor: string, node: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } }>, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, endCursor?: string | null, totalCount: number } } };

export type GetProductQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetProductQuery = { __typename?: 'Query', product?: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } | null };

export type GetCartQueryVariables = Exact<{ [key: string]: never; }>;


export type GetCartQuery = { __typename?: 'Query', cart: { __typename?: 'Cart', id: string, totalPrice: number, items: Array<{ __typename?: 'CartItem', quantity: number, totalPrice: number, product: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } }> } };

export type AddToCartMutationVariables = Exact<{
  input: AddToCartInput;
}>;


export type AddToCartMutation = { __typename?: 'Mutation', addToCart: { __typename?: 'Cart', id: string, totalPrice: number, items: Array<{ __typename?: 'CartItem', quantity: number, totalPrice: number, product: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } }> } };

export type UpdateCartItemMutationVariables = Exact<{
  input: UpdateCartItemInput;
}>;


export type UpdateCartItemMutation = { __typename?: 'Mutation', updateCartItem: { __typename?: 'Cart', id: string, totalPrice: number, items: Array<{ __typename?: 'CartItem', quantity: number, totalPrice: number, product: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } }> } };

export type RemoveFromCartMutationVariables = Exact<{
  productId: Scalars['ID']['input'];
}>;


export type RemoveFromCartMutation = { __typename?: 'Mutation', removeFromCart: { __typename?: 'Cart', id: string, totalPrice: number, items: Array<{ __typename?: 'CartItem', quantity: number, totalPrice: number, product: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } }> } };

export type PlaceOrderMutationVariables = Exact<{
  input: PlaceOrderInput;
}>;


export type PlaceOrderMutation = { __typename?: 'Mutation', placeOrder: { __typename?: 'Order', id: string, customerName: string, customerEmail: string, shippingAddress: string, totalPrice: number, state: OrderState, createdAt: string } };

export type ClearCartMutationVariables = Exact<{ [key: string]: never; }>;


export type ClearCartMutation = { __typename?: 'Mutation', clearCart: { __typename?: 'Cart', id: string, totalPrice: number, items: Array<{ __typename?: 'CartItem', quantity: number, totalPrice: number, product: { __typename?: 'Product', id: string, name: string, description?: string | null, imageData?: string | null, pricePerUnit: number, countInStock: number, state: ProductState, createdAt: string, updatedAt: string } }> } };


export const GetProductsAdminDocument = gql`
    query GetProductsAdmin($first: Int, $after: String, $filter: ProductFilterInput) {
  products(first: $first, after: $after, filter: $filter) {
    edges {
      node {
        id
        name
        description
        imageData
        pricePerUnit
        countInStock
        state
        createdAt
        updatedAt
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
      totalCount
    }
  }
}
    `;

/**
 * __useGetProductsAdminQuery__
 *
 * To run a query within a React component, call `useGetProductsAdminQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetProductsAdminQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetProductsAdminQuery({
 *   variables: {
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      filter: // value for 'filter'
 *   },
 * });
 */
export function useGetProductsAdminQuery(baseOptions?: Apollo.QueryHookOptions<GetProductsAdminQuery, GetProductsAdminQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetProductsAdminQuery, GetProductsAdminQueryVariables>(GetProductsAdminDocument, options);
      }
export function useGetProductsAdminLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetProductsAdminQuery, GetProductsAdminQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetProductsAdminQuery, GetProductsAdminQueryVariables>(GetProductsAdminDocument, options);
        }
// @ts-ignore
export function useGetProductsAdminSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetProductsAdminQuery, GetProductsAdminQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductsAdminQuery, GetProductsAdminQueryVariables>;
export function useGetProductsAdminSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductsAdminQuery, GetProductsAdminQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductsAdminQuery | undefined, GetProductsAdminQueryVariables>;
export function useGetProductsAdminSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductsAdminQuery, GetProductsAdminQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetProductsAdminQuery, GetProductsAdminQueryVariables>(GetProductsAdminDocument, options);
        }
export type GetProductsAdminQueryHookResult = ReturnType<typeof useGetProductsAdminQuery>;
export type GetProductsAdminLazyQueryHookResult = ReturnType<typeof useGetProductsAdminLazyQuery>;
export type GetProductsAdminSuspenseQueryHookResult = ReturnType<typeof useGetProductsAdminSuspenseQuery>;
export type GetProductsAdminQueryResult = Apollo.QueryResult<GetProductsAdminQuery, GetProductsAdminQueryVariables>;
export const GetProductAdminDocument = gql`
    query GetProductAdmin($id: ID!) {
  product(id: $id) {
    id
    name
    description
    imageData
    pricePerUnit
    countInStock
    state
    createdAt
    updatedAt
  }
}
    `;

/**
 * __useGetProductAdminQuery__
 *
 * To run a query within a React component, call `useGetProductAdminQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetProductAdminQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetProductAdminQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetProductAdminQuery(baseOptions: Apollo.QueryHookOptions<GetProductAdminQuery, GetProductAdminQueryVariables> & ({ variables: GetProductAdminQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetProductAdminQuery, GetProductAdminQueryVariables>(GetProductAdminDocument, options);
      }
export function useGetProductAdminLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetProductAdminQuery, GetProductAdminQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetProductAdminQuery, GetProductAdminQueryVariables>(GetProductAdminDocument, options);
        }
// @ts-ignore
export function useGetProductAdminSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetProductAdminQuery, GetProductAdminQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductAdminQuery, GetProductAdminQueryVariables>;
export function useGetProductAdminSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductAdminQuery, GetProductAdminQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductAdminQuery | undefined, GetProductAdminQueryVariables>;
export function useGetProductAdminSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductAdminQuery, GetProductAdminQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetProductAdminQuery, GetProductAdminQueryVariables>(GetProductAdminDocument, options);
        }
export type GetProductAdminQueryHookResult = ReturnType<typeof useGetProductAdminQuery>;
export type GetProductAdminLazyQueryHookResult = ReturnType<typeof useGetProductAdminLazyQuery>;
export type GetProductAdminSuspenseQueryHookResult = ReturnType<typeof useGetProductAdminSuspenseQuery>;
export type GetProductAdminQueryResult = Apollo.QueryResult<GetProductAdminQuery, GetProductAdminQueryVariables>;
export const GetOrdersDocument = gql`
    query GetOrders($first: Int, $after: String, $filter: OrderFilterInput) {
  orders(first: $first, after: $after, filter: $filter) {
    edges {
      node {
        id
        customerName
        customerEmail
        shippingAddress
        items {
          product {
            id
            name
            pricePerUnit
          }
          quantity
          totalPrice
        }
        totalPrice
        state
        createdAt
        updatedAt
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
      totalCount
    }
  }
}
    `;

/**
 * __useGetOrdersQuery__
 *
 * To run a query within a React component, call `useGetOrdersQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetOrdersQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetOrdersQuery({
 *   variables: {
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      filter: // value for 'filter'
 *   },
 * });
 */
export function useGetOrdersQuery(baseOptions?: Apollo.QueryHookOptions<GetOrdersQuery, GetOrdersQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetOrdersQuery, GetOrdersQueryVariables>(GetOrdersDocument, options);
      }
export function useGetOrdersLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetOrdersQuery, GetOrdersQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetOrdersQuery, GetOrdersQueryVariables>(GetOrdersDocument, options);
        }
// @ts-ignore
export function useGetOrdersSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetOrdersQuery, GetOrdersQueryVariables>): Apollo.UseSuspenseQueryResult<GetOrdersQuery, GetOrdersQueryVariables>;
export function useGetOrdersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetOrdersQuery, GetOrdersQueryVariables>): Apollo.UseSuspenseQueryResult<GetOrdersQuery | undefined, GetOrdersQueryVariables>;
export function useGetOrdersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetOrdersQuery, GetOrdersQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetOrdersQuery, GetOrdersQueryVariables>(GetOrdersDocument, options);
        }
export type GetOrdersQueryHookResult = ReturnType<typeof useGetOrdersQuery>;
export type GetOrdersLazyQueryHookResult = ReturnType<typeof useGetOrdersLazyQuery>;
export type GetOrdersSuspenseQueryHookResult = ReturnType<typeof useGetOrdersSuspenseQuery>;
export type GetOrdersQueryResult = Apollo.QueryResult<GetOrdersQuery, GetOrdersQueryVariables>;
export const GetOrderDocument = gql`
    query GetOrder($id: ID!) {
  order(id: $id) {
    id
    customerName
    customerEmail
    shippingAddress
    items {
      product {
        id
        name
        pricePerUnit
      }
      quantity
      totalPrice
    }
    totalPrice
    state
    createdAt
    updatedAt
  }
}
    `;

/**
 * __useGetOrderQuery__
 *
 * To run a query within a React component, call `useGetOrderQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetOrderQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetOrderQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetOrderQuery(baseOptions: Apollo.QueryHookOptions<GetOrderQuery, GetOrderQueryVariables> & ({ variables: GetOrderQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetOrderQuery, GetOrderQueryVariables>(GetOrderDocument, options);
      }
export function useGetOrderLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetOrderQuery, GetOrderQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetOrderQuery, GetOrderQueryVariables>(GetOrderDocument, options);
        }
// @ts-ignore
export function useGetOrderSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetOrderQuery, GetOrderQueryVariables>): Apollo.UseSuspenseQueryResult<GetOrderQuery, GetOrderQueryVariables>;
export function useGetOrderSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetOrderQuery, GetOrderQueryVariables>): Apollo.UseSuspenseQueryResult<GetOrderQuery | undefined, GetOrderQueryVariables>;
export function useGetOrderSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetOrderQuery, GetOrderQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetOrderQuery, GetOrderQueryVariables>(GetOrderDocument, options);
        }
export type GetOrderQueryHookResult = ReturnType<typeof useGetOrderQuery>;
export type GetOrderLazyQueryHookResult = ReturnType<typeof useGetOrderLazyQuery>;
export type GetOrderSuspenseQueryHookResult = ReturnType<typeof useGetOrderSuspenseQuery>;
export type GetOrderQueryResult = Apollo.QueryResult<GetOrderQuery, GetOrderQueryVariables>;
export const CreateProductDocument = gql`
    mutation CreateProduct($input: CreateProductInput!) {
  createProduct(input: $input) {
    id
    name
    description
    imageData
    pricePerUnit
    countInStock
    state
    createdAt
    updatedAt
  }
}
    `;
export type CreateProductMutationFn = Apollo.MutationFunction<CreateProductMutation, CreateProductMutationVariables>;

/**
 * __useCreateProductMutation__
 *
 * To run a mutation, you first call `useCreateProductMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateProductMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createProductMutation, { data, loading, error }] = useCreateProductMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateProductMutation(baseOptions?: Apollo.MutationHookOptions<CreateProductMutation, CreateProductMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateProductMutation, CreateProductMutationVariables>(CreateProductDocument, options);
      }
export type CreateProductMutationHookResult = ReturnType<typeof useCreateProductMutation>;
export type CreateProductMutationResult = Apollo.MutationResult<CreateProductMutation>;
export type CreateProductMutationOptions = Apollo.BaseMutationOptions<CreateProductMutation, CreateProductMutationVariables>;
export const UpdateProductDocument = gql`
    mutation UpdateProduct($input: UpdateProductInput!) {
  updateProduct(input: $input) {
    id
    name
    description
    imageData
    pricePerUnit
    countInStock
    state
    createdAt
    updatedAt
  }
}
    `;
export type UpdateProductMutationFn = Apollo.MutationFunction<UpdateProductMutation, UpdateProductMutationVariables>;

/**
 * __useUpdateProductMutation__
 *
 * To run a mutation, you first call `useUpdateProductMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateProductMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateProductMutation, { data, loading, error }] = useUpdateProductMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateProductMutation(baseOptions?: Apollo.MutationHookOptions<UpdateProductMutation, UpdateProductMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateProductMutation, UpdateProductMutationVariables>(UpdateProductDocument, options);
      }
export type UpdateProductMutationHookResult = ReturnType<typeof useUpdateProductMutation>;
export type UpdateProductMutationResult = Apollo.MutationResult<UpdateProductMutation>;
export type UpdateProductMutationOptions = Apollo.BaseMutationOptions<UpdateProductMutation, UpdateProductMutationVariables>;
export const PutProductOnShelfDocument = gql`
    mutation PutProductOnShelf($id: ID!) {
  putProductOnShelf(id: $id) {
    id
    state
  }
}
    `;
export type PutProductOnShelfMutationFn = Apollo.MutationFunction<PutProductOnShelfMutation, PutProductOnShelfMutationVariables>;

/**
 * __usePutProductOnShelfMutation__
 *
 * To run a mutation, you first call `usePutProductOnShelfMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `usePutProductOnShelfMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [putProductOnShelfMutation, { data, loading, error }] = usePutProductOnShelfMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function usePutProductOnShelfMutation(baseOptions?: Apollo.MutationHookOptions<PutProductOnShelfMutation, PutProductOnShelfMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<PutProductOnShelfMutation, PutProductOnShelfMutationVariables>(PutProductOnShelfDocument, options);
      }
export type PutProductOnShelfMutationHookResult = ReturnType<typeof usePutProductOnShelfMutation>;
export type PutProductOnShelfMutationResult = Apollo.MutationResult<PutProductOnShelfMutation>;
export type PutProductOnShelfMutationOptions = Apollo.BaseMutationOptions<PutProductOnShelfMutation, PutProductOnShelfMutationVariables>;
export const TakeProductOffShelfDocument = gql`
    mutation TakeProductOffShelf($id: ID!) {
  takeProductOffShelf(id: $id) {
    id
    state
  }
}
    `;
export type TakeProductOffShelfMutationFn = Apollo.MutationFunction<TakeProductOffShelfMutation, TakeProductOffShelfMutationVariables>;

/**
 * __useTakeProductOffShelfMutation__
 *
 * To run a mutation, you first call `useTakeProductOffShelfMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useTakeProductOffShelfMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [takeProductOffShelfMutation, { data, loading, error }] = useTakeProductOffShelfMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useTakeProductOffShelfMutation(baseOptions?: Apollo.MutationHookOptions<TakeProductOffShelfMutation, TakeProductOffShelfMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<TakeProductOffShelfMutation, TakeProductOffShelfMutationVariables>(TakeProductOffShelfDocument, options);
      }
export type TakeProductOffShelfMutationHookResult = ReturnType<typeof useTakeProductOffShelfMutation>;
export type TakeProductOffShelfMutationResult = Apollo.MutationResult<TakeProductOffShelfMutation>;
export type TakeProductOffShelfMutationOptions = Apollo.BaseMutationOptions<TakeProductOffShelfMutation, TakeProductOffShelfMutationVariables>;
export const RemoveProductDocument = gql`
    mutation RemoveProduct($id: ID!) {
  removeProduct(id: $id)
}
    `;
export type RemoveProductMutationFn = Apollo.MutationFunction<RemoveProductMutation, RemoveProductMutationVariables>;

/**
 * __useRemoveProductMutation__
 *
 * To run a mutation, you first call `useRemoveProductMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRemoveProductMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [removeProductMutation, { data, loading, error }] = useRemoveProductMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useRemoveProductMutation(baseOptions?: Apollo.MutationHookOptions<RemoveProductMutation, RemoveProductMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RemoveProductMutation, RemoveProductMutationVariables>(RemoveProductDocument, options);
      }
export type RemoveProductMutationHookResult = ReturnType<typeof useRemoveProductMutation>;
export type RemoveProductMutationResult = Apollo.MutationResult<RemoveProductMutation>;
export type RemoveProductMutationOptions = Apollo.BaseMutationOptions<RemoveProductMutation, RemoveProductMutationVariables>;
export const ShipOrderDocument = gql`
    mutation ShipOrder($id: ID!) {
  shipOrder(id: $id) {
    id
    state
    updatedAt
  }
}
    `;
export type ShipOrderMutationFn = Apollo.MutationFunction<ShipOrderMutation, ShipOrderMutationVariables>;

/**
 * __useShipOrderMutation__
 *
 * To run a mutation, you first call `useShipOrderMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useShipOrderMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [shipOrderMutation, { data, loading, error }] = useShipOrderMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useShipOrderMutation(baseOptions?: Apollo.MutationHookOptions<ShipOrderMutation, ShipOrderMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ShipOrderMutation, ShipOrderMutationVariables>(ShipOrderDocument, options);
      }
export type ShipOrderMutationHookResult = ReturnType<typeof useShipOrderMutation>;
export type ShipOrderMutationResult = Apollo.MutationResult<ShipOrderMutation>;
export type ShipOrderMutationOptions = Apollo.BaseMutationOptions<ShipOrderMutation, ShipOrderMutationVariables>;
export const CompleteOrderDocument = gql`
    mutation CompleteOrder($id: ID!) {
  completeOrder(id: $id) {
    id
    state
    updatedAt
  }
}
    `;
export type CompleteOrderMutationFn = Apollo.MutationFunction<CompleteOrderMutation, CompleteOrderMutationVariables>;

/**
 * __useCompleteOrderMutation__
 *
 * To run a mutation, you first call `useCompleteOrderMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCompleteOrderMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [completeOrderMutation, { data, loading, error }] = useCompleteOrderMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useCompleteOrderMutation(baseOptions?: Apollo.MutationHookOptions<CompleteOrderMutation, CompleteOrderMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CompleteOrderMutation, CompleteOrderMutationVariables>(CompleteOrderDocument, options);
      }
export type CompleteOrderMutationHookResult = ReturnType<typeof useCompleteOrderMutation>;
export type CompleteOrderMutationResult = Apollo.MutationResult<CompleteOrderMutation>;
export type CompleteOrderMutationOptions = Apollo.BaseMutationOptions<CompleteOrderMutation, CompleteOrderMutationVariables>;
export const CancelOrderDocument = gql`
    mutation CancelOrder($id: ID!) {
  cancelOrder(id: $id) {
    id
    state
    updatedAt
  }
}
    `;
export type CancelOrderMutationFn = Apollo.MutationFunction<CancelOrderMutation, CancelOrderMutationVariables>;

/**
 * __useCancelOrderMutation__
 *
 * To run a mutation, you first call `useCancelOrderMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCancelOrderMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [cancelOrderMutation, { data, loading, error }] = useCancelOrderMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useCancelOrderMutation(baseOptions?: Apollo.MutationHookOptions<CancelOrderMutation, CancelOrderMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CancelOrderMutation, CancelOrderMutationVariables>(CancelOrderDocument, options);
      }
export type CancelOrderMutationHookResult = ReturnType<typeof useCancelOrderMutation>;
export type CancelOrderMutationResult = Apollo.MutationResult<CancelOrderMutation>;
export type CancelOrderMutationOptions = Apollo.BaseMutationOptions<CancelOrderMutation, CancelOrderMutationVariables>;
export const GetProductsDocument = gql`
    query GetProducts($first: Int, $after: String) {
  products(first: $first, after: $after) {
    edges {
      node {
        id
        name
        description
        imageData
        pricePerUnit
        countInStock
        state
        createdAt
        updatedAt
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
      totalCount
    }
  }
}
    `;

/**
 * __useGetProductsQuery__
 *
 * To run a query within a React component, call `useGetProductsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetProductsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetProductsQuery({
 *   variables: {
 *      first: // value for 'first'
 *      after: // value for 'after'
 *   },
 * });
 */
export function useGetProductsQuery(baseOptions?: Apollo.QueryHookOptions<GetProductsQuery, GetProductsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetProductsQuery, GetProductsQueryVariables>(GetProductsDocument, options);
      }
export function useGetProductsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetProductsQuery, GetProductsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetProductsQuery, GetProductsQueryVariables>(GetProductsDocument, options);
        }
// @ts-ignore
export function useGetProductsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetProductsQuery, GetProductsQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductsQuery, GetProductsQueryVariables>;
export function useGetProductsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductsQuery, GetProductsQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductsQuery | undefined, GetProductsQueryVariables>;
export function useGetProductsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductsQuery, GetProductsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetProductsQuery, GetProductsQueryVariables>(GetProductsDocument, options);
        }
export type GetProductsQueryHookResult = ReturnType<typeof useGetProductsQuery>;
export type GetProductsLazyQueryHookResult = ReturnType<typeof useGetProductsLazyQuery>;
export type GetProductsSuspenseQueryHookResult = ReturnType<typeof useGetProductsSuspenseQuery>;
export type GetProductsQueryResult = Apollo.QueryResult<GetProductsQuery, GetProductsQueryVariables>;
export const GetProductDocument = gql`
    query GetProduct($id: ID!) {
  product(id: $id) {
    id
    name
    description
    imageData
    pricePerUnit
    countInStock
    state
    createdAt
    updatedAt
  }
}
    `;

/**
 * __useGetProductQuery__
 *
 * To run a query within a React component, call `useGetProductQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetProductQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetProductQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetProductQuery(baseOptions: Apollo.QueryHookOptions<GetProductQuery, GetProductQueryVariables> & ({ variables: GetProductQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetProductQuery, GetProductQueryVariables>(GetProductDocument, options);
      }
export function useGetProductLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetProductQuery, GetProductQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetProductQuery, GetProductQueryVariables>(GetProductDocument, options);
        }
// @ts-ignore
export function useGetProductSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetProductQuery, GetProductQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductQuery, GetProductQueryVariables>;
export function useGetProductSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductQuery, GetProductQueryVariables>): Apollo.UseSuspenseQueryResult<GetProductQuery | undefined, GetProductQueryVariables>;
export function useGetProductSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetProductQuery, GetProductQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetProductQuery, GetProductQueryVariables>(GetProductDocument, options);
        }
export type GetProductQueryHookResult = ReturnType<typeof useGetProductQuery>;
export type GetProductLazyQueryHookResult = ReturnType<typeof useGetProductLazyQuery>;
export type GetProductSuspenseQueryHookResult = ReturnType<typeof useGetProductSuspenseQuery>;
export type GetProductQueryResult = Apollo.QueryResult<GetProductQuery, GetProductQueryVariables>;
export const GetCartDocument = gql`
    query GetCart {
  cart {
    id
    items {
      product {
        id
        name
        description
        imageData
        pricePerUnit
        countInStock
        state
        createdAt
        updatedAt
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
    `;

/**
 * __useGetCartQuery__
 *
 * To run a query within a React component, call `useGetCartQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetCartQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetCartQuery({
 *   variables: {
 *   },
 * });
 */
export function useGetCartQuery(baseOptions?: Apollo.QueryHookOptions<GetCartQuery, GetCartQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetCartQuery, GetCartQueryVariables>(GetCartDocument, options);
      }
export function useGetCartLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetCartQuery, GetCartQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetCartQuery, GetCartQueryVariables>(GetCartDocument, options);
        }
// @ts-ignore
export function useGetCartSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetCartQuery, GetCartQueryVariables>): Apollo.UseSuspenseQueryResult<GetCartQuery, GetCartQueryVariables>;
export function useGetCartSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCartQuery, GetCartQueryVariables>): Apollo.UseSuspenseQueryResult<GetCartQuery | undefined, GetCartQueryVariables>;
export function useGetCartSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCartQuery, GetCartQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetCartQuery, GetCartQueryVariables>(GetCartDocument, options);
        }
export type GetCartQueryHookResult = ReturnType<typeof useGetCartQuery>;
export type GetCartLazyQueryHookResult = ReturnType<typeof useGetCartLazyQuery>;
export type GetCartSuspenseQueryHookResult = ReturnType<typeof useGetCartSuspenseQuery>;
export type GetCartQueryResult = Apollo.QueryResult<GetCartQuery, GetCartQueryVariables>;
export const AddToCartDocument = gql`
    mutation AddToCart($input: AddToCartInput!) {
  addToCart(input: $input) {
    id
    items {
      product {
        id
        name
        description
        imageData
        pricePerUnit
        countInStock
        state
        createdAt
        updatedAt
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
    `;
export type AddToCartMutationFn = Apollo.MutationFunction<AddToCartMutation, AddToCartMutationVariables>;

/**
 * __useAddToCartMutation__
 *
 * To run a mutation, you first call `useAddToCartMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddToCartMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addToCartMutation, { data, loading, error }] = useAddToCartMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddToCartMutation(baseOptions?: Apollo.MutationHookOptions<AddToCartMutation, AddToCartMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddToCartMutation, AddToCartMutationVariables>(AddToCartDocument, options);
      }
export type AddToCartMutationHookResult = ReturnType<typeof useAddToCartMutation>;
export type AddToCartMutationResult = Apollo.MutationResult<AddToCartMutation>;
export type AddToCartMutationOptions = Apollo.BaseMutationOptions<AddToCartMutation, AddToCartMutationVariables>;
export const UpdateCartItemDocument = gql`
    mutation UpdateCartItem($input: UpdateCartItemInput!) {
  updateCartItem(input: $input) {
    id
    items {
      product {
        id
        name
        description
        imageData
        pricePerUnit
        countInStock
        state
        createdAt
        updatedAt
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
    `;
export type UpdateCartItemMutationFn = Apollo.MutationFunction<UpdateCartItemMutation, UpdateCartItemMutationVariables>;

/**
 * __useUpdateCartItemMutation__
 *
 * To run a mutation, you first call `useUpdateCartItemMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateCartItemMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateCartItemMutation, { data, loading, error }] = useUpdateCartItemMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateCartItemMutation(baseOptions?: Apollo.MutationHookOptions<UpdateCartItemMutation, UpdateCartItemMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateCartItemMutation, UpdateCartItemMutationVariables>(UpdateCartItemDocument, options);
      }
export type UpdateCartItemMutationHookResult = ReturnType<typeof useUpdateCartItemMutation>;
export type UpdateCartItemMutationResult = Apollo.MutationResult<UpdateCartItemMutation>;
export type UpdateCartItemMutationOptions = Apollo.BaseMutationOptions<UpdateCartItemMutation, UpdateCartItemMutationVariables>;
export const RemoveFromCartDocument = gql`
    mutation RemoveFromCart($productId: ID!) {
  removeFromCart(productId: $productId) {
    id
    items {
      product {
        id
        name
        description
        imageData
        pricePerUnit
        countInStock
        state
        createdAt
        updatedAt
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
    `;
export type RemoveFromCartMutationFn = Apollo.MutationFunction<RemoveFromCartMutation, RemoveFromCartMutationVariables>;

/**
 * __useRemoveFromCartMutation__
 *
 * To run a mutation, you first call `useRemoveFromCartMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRemoveFromCartMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [removeFromCartMutation, { data, loading, error }] = useRemoveFromCartMutation({
 *   variables: {
 *      productId: // value for 'productId'
 *   },
 * });
 */
export function useRemoveFromCartMutation(baseOptions?: Apollo.MutationHookOptions<RemoveFromCartMutation, RemoveFromCartMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RemoveFromCartMutation, RemoveFromCartMutationVariables>(RemoveFromCartDocument, options);
      }
export type RemoveFromCartMutationHookResult = ReturnType<typeof useRemoveFromCartMutation>;
export type RemoveFromCartMutationResult = Apollo.MutationResult<RemoveFromCartMutation>;
export type RemoveFromCartMutationOptions = Apollo.BaseMutationOptions<RemoveFromCartMutation, RemoveFromCartMutationVariables>;
export const PlaceOrderDocument = gql`
    mutation PlaceOrder($input: PlaceOrderInput!) {
  placeOrder(input: $input) {
    id
    customerName
    customerEmail
    shippingAddress
    totalPrice
    state
    createdAt
  }
}
    `;
export type PlaceOrderMutationFn = Apollo.MutationFunction<PlaceOrderMutation, PlaceOrderMutationVariables>;

/**
 * __usePlaceOrderMutation__
 *
 * To run a mutation, you first call `usePlaceOrderMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `usePlaceOrderMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [placeOrderMutation, { data, loading, error }] = usePlaceOrderMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function usePlaceOrderMutation(baseOptions?: Apollo.MutationHookOptions<PlaceOrderMutation, PlaceOrderMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<PlaceOrderMutation, PlaceOrderMutationVariables>(PlaceOrderDocument, options);
      }
export type PlaceOrderMutationHookResult = ReturnType<typeof usePlaceOrderMutation>;
export type PlaceOrderMutationResult = Apollo.MutationResult<PlaceOrderMutation>;
export type PlaceOrderMutationOptions = Apollo.BaseMutationOptions<PlaceOrderMutation, PlaceOrderMutationVariables>;
export const ClearCartDocument = gql`
    mutation ClearCart {
  clearCart {
    id
    items {
      product {
        id
        name
        description
        imageData
        pricePerUnit
        countInStock
        state
        createdAt
        updatedAt
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
    `;
export type ClearCartMutationFn = Apollo.MutationFunction<ClearCartMutation, ClearCartMutationVariables>;

/**
 * __useClearCartMutation__
 *
 * To run a mutation, you first call `useClearCartMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useClearCartMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [clearCartMutation, { data, loading, error }] = useClearCartMutation({
 *   variables: {
 *   },
 * });
 */
export function useClearCartMutation(baseOptions?: Apollo.MutationHookOptions<ClearCartMutation, ClearCartMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ClearCartMutation, ClearCartMutationVariables>(ClearCartDocument, options);
      }
export type ClearCartMutationHookResult = ReturnType<typeof useClearCartMutation>;
export type ClearCartMutationResult = Apollo.MutationResult<ClearCartMutation>;
export type ClearCartMutationOptions = Apollo.BaseMutationOptions<ClearCartMutation, ClearCartMutationVariables>;