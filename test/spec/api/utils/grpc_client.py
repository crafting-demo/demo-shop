"""gRPC client utilities for testing.

Note: This module assumes the protobuf files have been compiled to Python.
Run: python -m grpc_tools.protoc -I../../src/apis/proto --python_out=./proto --grpc_python_out=./proto ../../src/apis/proto/demoshop/v1/*.proto
"""
import grpc
from typing import Optional, List, Any

# Note: These imports will work after proto files are compiled
# For now, we'll use placeholders and type hints
try:
    from proto.demoshop.v1 import transaction_pb2, transaction_pb2_grpc
except ImportError:
    # Placeholder for when protos aren't compiled yet
    transaction_pb2 = None
    transaction_pb2_grpc = None


class GRPCClient:
    """Base gRPC client."""

    def __init__(self, host: str, port: int):
        """Initialize gRPC client.
        
        Args:
            host: gRPC server host
            port: gRPC server port
        """
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f"{host}:{port}")

    def close(self):
        """Close the channel."""
        if self.channel:
            self.channel.close()


class InventoryServiceClient(GRPCClient):
    """gRPC client for InventoryService."""

    def __init__(self, host: str, port: int):
        """Initialize InventoryService client."""
        super().__init__(host, port)
        if transaction_pb2_grpc:
            self.stub = transaction_pb2_grpc.InventoryServiceStub(self.channel)
        else:
            self.stub = None

    def query_products(
        self,
        first: int = 20,
        after: Optional[str] = None,
        state_filter: Optional[int] = None,
    ) -> Any:
        """Query products.
        
        Args:
            first: Number of products to fetch
            after: Cursor for pagination
            state_filter: Filter by state (1=AVAILABLE, 2=OFF_SHELF)
            
        Returns:
            QueryProductsResponse
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled. Run proto compilation first.")
        
        request = transaction_pb2.QueryProductsRequest(
            pagination=transaction_pb2.PaginationRequest(first=first, after=after or "")
        )
        if state_filter is not None:
            request.state_filter = state_filter
        
        return self.stub.QueryProducts(request)

    def get_product(self, product_id: str) -> Any:
        """Get product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.GetProductRequest(id=product_id)
        response = self.stub.GetProduct(request)
        return response.product

    def create_product(
        self,
        name: str,
        price_per_unit: int,
        count_in_stock: int,
        description: str = "",
        image_data: bytes = b"",
        state: int = 1,  # AVAILABLE
    ) -> Any:
        """Create product.
        
        Args:
            name: Product name
            price_per_unit: Price in cents
            count_in_stock: Stock count
            description: Product description
            image_data: Image bytes
            state: Product state (1=AVAILABLE, 2=OFF_SHELF)
            
        Returns:
            CreateProductResponse
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.CreateProductRequest(
            name=name,
            description=description,
            image_data=image_data,
            price_per_unit=price_per_unit,
            count_in_stock=count_in_stock,
            state=state,
        )
        response = self.stub.CreateProduct(request)
        return response.product

    def update_product(
        self,
        product_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_data: Optional[bytes] = None,
        price_per_unit: Optional[int] = None,
        count_in_stock: Optional[int] = None,
        state: Optional[int] = None,
    ) -> Any:
        """Update product.
        
        Args:
            product_id: Product ID
            name: New name
            description: New description
            image_data: New image bytes
            price_per_unit: New price
            count_in_stock: New stock count
            state: New state
            
        Returns:
            UpdateProductResponse
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.UpdateProductRequest(id=product_id)
        
        if name is not None:
            request.name.value = name
        if description is not None:
            request.description.value = description
        if image_data is not None:
            request.image_data.value = image_data
        if price_per_unit is not None:
            request.price_per_unit.value = price_per_unit
        if count_in_stock is not None:
            request.count_in_stock.value = count_in_stock
        if state is not None:
            request.state.value = state
        
        response = self.stub.UpdateProduct(request)
        return response.product

    def delete_product(self, product_id: str) -> Any:
        """Delete product.
        
        Args:
            product_id: Product ID
            
        Returns:
            DeleteProductResponse
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.DeleteProductRequest(id=product_id)
        return self.stub.DeleteProduct(request)


class CartServiceClient(GRPCClient):
    """gRPC client for CartService."""

    def __init__(self, host: str, port: int):
        """Initialize CartService client."""
        super().__init__(host, port)
        if transaction_pb2_grpc:
            self.stub = transaction_pb2_grpc.CartServiceStub(self.channel)
        else:
            self.stub = None

    def get_cart(self, cart_id: str) -> Any:
        """Get cart by ID.
        
        Args:
            cart_id: Cart ID
            
        Returns:
            Cart
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.GetCartRequest(cart_id=cart_id)
        response = self.stub.GetCart(request)
        return response.cart

    def add_product_to_cart(
        self, cart_id: str, product_id: str, quantity: int
    ) -> Any:
        """Add product to cart.
        
        Args:
            cart_id: Cart ID
            product_id: Product ID
            quantity: Quantity to add
            
        Returns:
            Cart
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.AddProductToCartRequest(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )
        response = self.stub.AddProductToCart(request)
        return response.cart

    def update_product_in_cart(
        self, cart_id: str, product_id: str, quantity: int
    ) -> Any:
        """Update product quantity in cart.
        
        Args:
            cart_id: Cart ID
            product_id: Product ID
            quantity: New quantity (0 to remove)
            
        Returns:
            Cart
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.UpdateProductInCartRequest(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )
        response = self.stub.UpdateProductInCart(request)
        return response.cart

    def clear_cart(self, cart_id: str) -> Any:
        """Clear cart.
        
        Args:
            cart_id: Cart ID
            
        Returns:
            ClearCartResponse
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.ClearCartRequest(cart_id=cart_id)
        return self.stub.ClearCart(request)


class OrderServiceClient(GRPCClient):
    """gRPC client for OrderService."""

    def __init__(self, host: str, port: int):
        """Initialize OrderService client."""
        super().__init__(host, port)
        if transaction_pb2_grpc:
            self.stub = transaction_pb2_grpc.OrderServiceStub(self.channel)
        else:
            self.stub = None

    def create_order(
        self, 
        cart_id: str, 
        customer_name: str = "Test Customer",
        customer_email: str = "test@example.com",
        shipping_address: str = "Test Address"
    ) -> Any:
        """Create order from cart.
        
        Args:
            cart_id: Cart ID
            customer_name: Customer name
            customer_email: Customer email
            shipping_address: Shipping address
            
        Returns:
            Order
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.CreateOrderRequest(
            cart_id=cart_id,
            customer_name=customer_name,
            customer_email=customer_email,
            shipping_address=shipping_address
        )
        response = self.stub.CreateOrder(request)
        return response.order

    def query_orders(
        self,
        first: int = 20,
        after: Optional[str] = None,
        state_filter: Optional[int] = None,
    ) -> Any:
        """Query orders.
        
        Args:
            first: Number of orders to fetch
            after: Cursor for pagination
            state_filter: Filter by state (1=PROCESSING, 2=SHIPPED, 3=COMPLETED, 4=CANCELED)
            
        Returns:
            QueryOrdersResponse
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.QueryOrdersRequest(
            pagination=transaction_pb2.PaginationRequest(first=first, after=after or "")
        )
        if state_filter is not None:
            request.state_filter.value = state_filter
        
        return self.stub.QueryOrders(request)

    def get_order(self, order_id: str) -> Any:
        """Get order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.GetOrderRequest(id=order_id)
        response = self.stub.GetOrder(request)
        return response.order

    def update_order(self, order_id: str, state: int) -> Any:
        """Update order state.
        
        Args:
            order_id: Order ID
            state: New state (1=PROCESSING, 2=SHIPPED, 3=COMPLETED, 4=CANCELED)
            
        Returns:
            UpdateOrderResponse
        """
        if not self.stub:
            raise RuntimeError("Protobuf stubs not compiled.")
        
        request = transaction_pb2.UpdateOrderRequest(
            id=order_id,
            state=state,
        )
        response = self.stub.UpdateOrder(request)
        return response.order
