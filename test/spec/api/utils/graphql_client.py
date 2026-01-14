"""GraphQL client utilities for testing."""
import json
from typing import Any, Dict, Optional

import requests


class GraphQLClient:
    """Base GraphQL client."""

    def __init__(self, url: str, timeout: int = 30):
        """Initialize GraphQL client.
        
        Args:
            url: GraphQL endpoint URL
            timeout: Request timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def execute(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute GraphQL query or mutation.
        
        Args:
            query: GraphQL query or mutation string
            variables: Query variables
            operation_name: Operation name for multi-operation documents
            
        Returns:
            Response data dictionary
            
        Raises:
            requests.HTTPError: If request fails
            AssertionError: If GraphQL errors are present
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        response = self.session.post(
            self.url,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        result = response.json()
        
        # Check for GraphQL errors
        if "errors" in result:
            error_messages = [err.get("message", str(err)) for err in result["errors"]]
            raise AssertionError(f"GraphQL errors: {', '.join(error_messages)}")
        
        return result

    def execute_raw(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> requests.Response:
        """Execute GraphQL query and return raw response.
        
        Useful for testing error cases where you expect errors.
        
        Args:
            query: GraphQL query or mutation string
            variables: Query variables
            operation_name: Operation name
            
        Returns:
            Raw requests.Response object
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        return self.session.post(
            self.url,
            json=payload,
            timeout=self.timeout,
        )

    def close(self):
        """Close the session."""
        self.session.close()


class CustomerGraphQLClient(GraphQLClient):
    """GraphQL client for customer-facing API."""

    def query_products(
        self, first: int = 20, after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query products list.
        
        Args:
            first: Number of products to fetch
            after: Cursor for pagination
            
        Returns:
            Products query result
        """
        query = """
            query QueryProducts($first: Int!, $after: String) {
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
                        hasPreviousPage
                        startCursor
                        endCursor
                        totalCount
                    }
                }
            }
        """
        variables = {"first": first}
        if after:
            variables["after"] = after
        
        return self.execute(query, variables)

    def query_product(self, product_id: str) -> Dict[str, Any]:
        """Query single product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product query result
        """
        query = """
            query QueryProduct($id: ID!) {
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
        """
        return self.execute(query, {"id": product_id})

    def query_cart(self) -> Dict[str, Any]:
        """Query cart.
        
        Returns:
            Cart query result
        """
        query = """
            query QueryCart {
                cart {
                    id
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
                }
            }
        """
        return self.execute(query)

    def add_to_cart(self, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        """Add product to cart.
        
        Args:
            product_id: Product ID to add
            quantity: Quantity to add
            
        Returns:
            Cart mutation result
        """
        mutation = """
            mutation AddToCart($input: AddToCartInput!) {
                addToCart(input: $input) {
                    id
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
                }
            }
        """
        variables = {
            "input": {
                "productId": product_id,
                "quantity": quantity,
            }
        }
        return self.execute(mutation, variables)

    def update_cart_item(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Update cart item quantity.
        
        Args:
            product_id: Product ID to update
            quantity: New quantity
            
        Returns:
            Cart mutation result
        """
        mutation = """
            mutation UpdateCartItem($input: UpdateCartItemInput!) {
                updateCartItem(input: $input) {
                    id
                    items {
                        product {
                            id
                            name
                        }
                        quantity
                        totalPrice
                    }
                    totalPrice
                }
            }
        """
        variables = {
            "input": {
                "productId": product_id,
                "quantity": quantity,
            }
        }
        return self.execute(mutation, variables)

    def remove_from_cart(self, product_id: str) -> Dict[str, Any]:
        """Remove product from cart.
        
        Args:
            product_id: Product ID to remove
            
        Returns:
            Cart mutation result
        """
        mutation = """
            mutation RemoveFromCart($productId: ID!) {
                removeFromCart(productId: $productId) {
                    id
                    items {
                        product {
                            id
                        }
                        quantity
                    }
                    totalPrice
                }
            }
        """
        return self.execute(mutation, {"productId": product_id})

    def clear_cart(self) -> Dict[str, Any]:
        """Clear all items from cart.
        
        Returns:
            Cart mutation result
        """
        mutation = """
            mutation ClearCart {
                clearCart {
                    id
                    items {
                        product {
                            id
                        }
                        quantity
                    }
                    totalPrice
                }
            }
        """
        return self.execute(mutation)

    def place_order(
        self, customer_name: str, customer_email: str, shipping_address: str
    ) -> Dict[str, Any]:
        """Place order.
        
        Args:
            customer_name: Customer name
            customer_email: Customer email
            shipping_address: Shipping address
            
        Returns:
            Order mutation result
        """
        mutation = """
            mutation PlaceOrder($input: PlaceOrderInput!) {
                placeOrder(input: $input) {
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
        """
        variables = {
            "input": {
                "customerName": customer_name,
                "customerEmail": customer_email,
                "shippingAddress": shipping_address,
            }
        }
        return self.execute(mutation, variables)


class AdminGraphQLClient(GraphQLClient):
    """GraphQL client for admin-facing API."""

    def query_products(
        self,
        first: int = 20,
        after: Optional[str] = None,
        state_filter: Optional[str] = None,
        search_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query products with filters.
        
        Args:
            first: Number of products to fetch
            after: Cursor for pagination
            state_filter: Filter by state (AVAILABLE, OFF_SHELF)
            search_name: Search by name
            
        Returns:
            Products query result
        """
        query = """
            query QueryProducts($first: Int!, $after: String, $filter: ProductFilterInput) {
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
        """
        variables = {"first": first}
        if after:
            variables["after"] = after
        
        filter_obj = {}
        if state_filter:
            filter_obj["state"] = state_filter
        if search_name:
            filter_obj["searchName"] = search_name
        if filter_obj:
            variables["filter"] = filter_obj
        
        return self.execute(query, variables)

    def create_product(
        self,
        name: str,
        price_per_unit: int,
        count_in_stock: int,
        description: Optional[str] = None,
        image_data: Optional[str] = None,
        state: str = "AVAILABLE",
    ) -> Dict[str, Any]:
        """Create product.
        
        Args:
            name: Product name
            price_per_unit: Price in cents
            count_in_stock: Stock count
            description: Product description
            image_data: Image data URI
            state: Product state
            
        Returns:
            Product mutation result
        """
        mutation = """
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
        """
        input_data = {
            "name": name,
            "pricePerUnit": price_per_unit,
            "countInStock": count_in_stock,
            "state": state,
        }
        if description:
            input_data["description"] = description
        if image_data:
            input_data["imageData"] = image_data
        
        return self.execute(mutation, {"input": input_data})

    def update_product(
        self,
        product_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_data: Optional[str] = None,
        price_per_unit: Optional[int] = None,
        count_in_stock: Optional[int] = None,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update product.
        
        Args:
            product_id: Product ID
            name: New name
            description: New description
            image_data: New image data
            price_per_unit: New price
            count_in_stock: New stock count
            state: New state
            
        Returns:
            Product mutation result
        """
        mutation = """
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
        """
        input_data = {"id": product_id}
        if name is not None:
            input_data["name"] = name
        if description is not None:
            input_data["description"] = description
        if image_data is not None:
            input_data["imageData"] = image_data
        if price_per_unit is not None:
            input_data["pricePerUnit"] = price_per_unit
        if count_in_stock is not None:
            input_data["countInStock"] = count_in_stock
        if state is not None:
            input_data["state"] = state
        
        return self.execute(mutation, {"input": input_data})

    def remove_product(self, product_id: str) -> Dict[str, Any]:
        """Remove product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Mutation result
        """
        mutation = """
            mutation RemoveProduct($id: ID!) {
                removeProduct(id: $id)
            }
        """
        return self.execute(mutation, {"id": product_id})

    def query_order(self, order_id: str) -> Dict[str, Any]:
        """Query single order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order query result
        """
        query = """
            query QueryOrder($id: ID!) {
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
        """
        return self.execute(query, {"id": order_id})

    def query_orders(
        self,
        first: int = 20,
        after: Optional[str] = None,
        state_filter: Optional[str] = None,
        customer_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query orders with filters.
        
        Args:
            first: Number of orders to fetch
            after: Cursor for pagination
            state_filter: Filter by state
            customer_email: Filter by customer email
            
        Returns:
            Orders query result
        """
        query = """
            query QueryOrders($first: Int!, $after: String, $filter: OrderFilterInput) {
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
        """
        variables = {"first": first}
        if after:
            variables["after"] = after
        
        filter_obj = {}
        if state_filter:
            filter_obj["state"] = state_filter
        if customer_email:
            filter_obj["customerEmail"] = customer_email
        if filter_obj:
            variables["filter"] = filter_obj
        
        return self.execute(query, variables)

    def ship_order(self, order_id: str) -> Dict[str, Any]:
        """Ship order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order mutation result
        """
        mutation = """
            mutation ShipOrder($id: ID!) {
                shipOrder(id: $id) {
                    id
                    state
                    updatedAt
                }
            }
        """
        return self.execute(mutation, {"id": order_id})

    def complete_order(self, order_id: str) -> Dict[str, Any]:
        """Complete order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order mutation result
        """
        mutation = """
            mutation CompleteOrder($id: ID!) {
                completeOrder(id: $id) {
                    id
                    state
                    updatedAt
                }
            }
        """
        return self.execute(mutation, {"id": order_id})

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order mutation result
        """
        mutation = """
            mutation CancelOrder($id: ID!) {
                cancelOrder(id: $id) {
                    id
                    state
                    updatedAt
                }
            }
        """
        return self.execute(mutation, {"id": order_id})
