import { gql } from '@apollo/client';

export const GET_PRODUCTS_ADMIN = gql`
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

export const GET_PRODUCT_ADMIN = gql`
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

export const GET_ORDERS = gql`
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

export const GET_ORDER = gql`
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

export const CREATE_PRODUCT = gql`
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

export const UPDATE_PRODUCT = gql`
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

export const PUT_PRODUCT_ON_SHELF = gql`
  mutation PutProductOnShelf($id: ID!) {
    putProductOnShelf(id: $id) {
      id
      state
    }
  }
`;

export const TAKE_PRODUCT_OFF_SHELF = gql`
  mutation TakeProductOffShelf($id: ID!) {
    takeProductOffShelf(id: $id) {
      id
      state
    }
  }
`;

export const REMOVE_PRODUCT = gql`
  mutation RemoveProduct($id: ID!) {
    removeProduct(id: $id)
  }
`;

export const SHIP_ORDER = gql`
  mutation ShipOrder($id: ID!) {
    shipOrder(id: $id) {
      id
      state
      updatedAt
    }
  }
`;

export const COMPLETE_ORDER = gql`
  mutation CompleteOrder($id: ID!) {
    completeOrder(id: $id) {
      id
      state
      updatedAt
    }
  }
`;

export const CANCEL_ORDER = gql`
  mutation CancelOrder($id: ID!) {
    cancelOrder(id: $id) {
      id
      state
      updatedAt
    }
  }
`;
