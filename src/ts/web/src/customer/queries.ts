import { gql } from '@apollo/client';

export const GET_PRODUCTS = gql`
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

export const GET_PRODUCT = gql`
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

export const GET_CART = gql`
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

export const ADD_TO_CART = gql`
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

export const UPDATE_CART_ITEM = gql`
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

export const REMOVE_FROM_CART = gql`
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

export const PLACE_ORDER = gql`
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

export const CLEAR_CART = gql`
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
