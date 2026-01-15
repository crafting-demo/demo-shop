"""
API-TC010: gRPC OrderService API

Test gRPC OrderService operations.
Tests CreateOrder, QueryOrders, GetOrder, UpdateOrder.
"""
import pytest
import uuid
from utils.grpc_client import OrderServiceClient, CartServiceClient, InventoryServiceClient


@pytest.mark.grpc
@pytest.mark.integration
class TestGRPCOrderService:
    """Test gRPC OrderService (API-TC010)."""

    def test_create_order_from_cart(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_ids: list
    ):
        """Step 1: CreateOrder - from cart with items."""
        cart_id = str(uuid.uuid4())
        
        # Add products to cart
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[0], 2)
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[1], 3)
        
        # Create order from cart
        order = order_grpc_client.create_order(cart_id=cart_id)
        
        assert order.id
        assert len(order.items) == 2
        assert order.state == 1  # PROCESSING = 1
        assert hasattr(order, 'created_at')
        assert hasattr(order, 'updated_at')

    def test_create_order_empty_cart(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient
    ):
        """Step 2: CreateOrder - from empty cart (should fail)."""
        cart_id = str(uuid.uuid4())
        
        # Get cart (creates empty cart)
        cart_grpc_client.get_cart(cart_id)
        
        # Try to create order from empty cart
        with pytest.raises(Exception) as exc_info:
            order_grpc_client.create_order(cart_id=cart_id)
        
        assert "FAILED_PRECONDITION" in str(exc_info.value) or "empty" in str(exc_info.value).lower()

    def test_create_order_invalid_email(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 3: CreateOrder - invalid email format."""
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        # Try to create order with invalid email
        with pytest.raises(Exception) as exc_info:
            order_grpc_client.create_order(
                cart_id=cart_id,
                customer_email="not-an-email",  # Invalid email
                customer_name="Test Customer",
                shipping_address="Test Address"
            )
        
        assert "INVALID_ARGUMENT" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()

    def test_create_order_missing_required_fields(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 4: CreateOrder - missing required fields."""
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        # Try to create order without customer name (empty string)
        with pytest.raises(Exception) as exc_info:
            order_grpc_client.create_order(
                cart_id=cart_id,
                customer_name="",  # Empty name
                customer_email="test@example.com",
                shipping_address="Test Address"
            )
        
        assert "INVALID_ARGUMENT" in str(exc_info.value) or "required" in str(exc_info.value).lower()

    def test_query_orders_all(self, order_grpc_client: OrderServiceClient):
        """Step 5: QueryOrders - all orders without filter."""
        response = order_grpc_client.query_orders(first=20)
        
        assert hasattr(response, 'orders')
        assert hasattr(response, 'page_info')
        assert hasattr(response, 'total_count')
        
        # Validate orders
        assert len(response.orders) <= 20
        
        for order in response.orders:
            assert order.id
            assert order.state in [1, 2, 3, 4]  # PROCESSING, SHIPPED, COMPLETED, CANCELED

    def test_query_orders_filter_processing(self, order_grpc_client: OrderServiceClient):
        """Step 6: QueryOrders - filter by PROCESSING state."""
        response = order_grpc_client.query_orders(first=50, state_filter=1)  # PROCESSING=1
        
        # All orders should be PROCESSING
        for order in response.orders:
            assert order.state == 1

    def test_query_orders_filter_shipped(self, order_grpc_client: OrderServiceClient):
        """Step 7: QueryOrders - filter by SHIPPED state."""
        response = order_grpc_client.query_orders(first=50, state_filter=2)  # SHIPPED=2
        
        # All orders should be SHIPPED
        for order in response.orders:
            assert order.state == 2

    def test_query_orders_filter_completed(self, order_grpc_client: OrderServiceClient):
        """Step 8: QueryOrders - filter by COMPLETED state."""
        response = order_grpc_client.query_orders(first=50, state_filter=3)  # COMPLETED=3
        
        # All orders should be COMPLETED
        for order in response.orders:
            assert order.state == 3

    def test_query_orders_filter_canceled(self, order_grpc_client: OrderServiceClient):
        """Step 9: QueryOrders - filter by CANCELED state."""
        response = order_grpc_client.query_orders(first=50, state_filter=4)  # CANCELED=4
        
        # All orders should be CANCELED
        for order in response.orders:
            assert order.state == 4

    def test_get_order_by_id(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 10: GetOrder - retrieve single order by ID."""
        # Create an order first
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        created_order = order_grpc_client.create_order(cart_id=cart_id)
        
        # Get the order
        order = order_grpc_client.get_order(created_order.id)
        
        assert order.id == created_order.id
    def test_get_order_not_found(self, order_grpc_client: OrderServiceClient):
        """Step 11: GetOrder - non-existent order."""
        with pytest.raises(Exception) as exc_info:
            order_grpc_client.get_order("non-existent-order-id-99999")
        
        assert "NOT_FOUND" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_update_order_processing_to_shipped(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 12: UpdateOrder - PROCESSING to SHIPPED."""
        # Create an order
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        order = order_grpc_client.create_order(cart_id=cart_id)
        
        # Update to SHIPPED
        updated = order_grpc_client.update_order(order.id, state=2)  # SHIPPED=2
        
        assert updated.state == 2

    def test_update_order_shipped_to_completed(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 13: UpdateOrder - SHIPPED to COMPLETED."""
        # Create and ship an order
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        order = order_grpc_client.create_order(cart_id=cart_id)
        order_grpc_client.update_order(order.id, state=2)  # Ship first
        
        # Complete the order
        updated = order_grpc_client.update_order(order.id, state=3)  # COMPLETED=3
        
        assert updated.state == 3

    def test_update_order_processing_to_canceled(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 14: UpdateOrder - PROCESSING to CANCELED."""
        # Create an order
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        order = order_grpc_client.create_order(cart_id=cart_id)
        
        # Cancel the order
        updated = order_grpc_client.update_order(order.id, state=4)  # CANCELED=4
        
        assert updated.state == 4

    def test_update_order_invalid_transition(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 15: UpdateOrder - invalid state transition."""
        # Create an order
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        order = order_grpc_client.create_order(cart_id=cart_id)
        
        # Try to complete without shipping first
        with pytest.raises(Exception) as exc_info:
            order_grpc_client.update_order(order.id, state=3)  # COMPLETED=3
        
        assert "FAILED_PRECONDITION" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()

    def test_update_completed_order(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 16: UpdateOrder - terminal state (should fail)."""
        # Create, ship, and complete an order
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 1)
        
        order = order_grpc_client.create_order(cart_id=cart_id)
        order_grpc_client.update_order(order.id, state=2)  # Ship
        order_grpc_client.update_order(order.id, state=3)  # Complete
        
        # Try to change completed order
        with pytest.raises(Exception) as exc_info:
            order_grpc_client.update_order(order.id, state=4)  # Try to cancel
        
        assert "FAILED_PRECONDITION" in str(exc_info.value) or "terminal" in str(exc_info.value).lower()

    def test_verify_product_snapshot_in_order(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        inventory_grpc_client: InventoryServiceClient
    ):
        """Step 17: Verify product snapshot immutability in order."""
        # Create a product
        product = inventory_grpc_client.create_product(
            name="Snapshot Order Test",
            price_per_unit=5000,
            count_in_stock=10
        )
        
        # Add to cart and create order
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, product.id, 2)
        
        order = order_grpc_client.create_order(cart_id=cart_id)
        
        original_price = order.items[0].price_at_purchase
        
        # Update product price
        inventory_grpc_client.update_product(product.id, price_per_unit=8000)
        
        # Get order again
        updated_order = order_grpc_client.get_order(order.id)
        
        # Snapshot price should not change (uses price_at_purchase)
        assert updated_order.items[0].price_at_purchase == original_price
        # But the live product price should have changed
        assert updated_order.items[0].product.price_per_unit == 8000

    def test_query_orders_pagination(self, order_grpc_client: OrderServiceClient):
        """Step 18: QueryOrders - pagination with cursor."""
        # First page
        first_response = order_grpc_client.query_orders(first=10)
        
        if not first_response.page_info.has_next_page:
            pytest.skip("Not enough orders for pagination test")
        
        # Second page
        end_cursor = first_response.page_info.end_cursor
        second_response = order_grpc_client.query_orders(first=10, after=end_cursor)
        
        # No duplicate orders
        first_ids = {o.id for o in first_response.orders}
        second_ids = {o.id for o in second_response.orders}
        assert len(first_ids & second_ids) == 0

    def test_verify_order_total_calculation(
        self,
        order_grpc_client: OrderServiceClient,
        cart_grpc_client: CartServiceClient,
        inventory_grpc_client: InventoryServiceClient
    ):
        """Step 19: Verify order total calculation."""
        # Create products with known prices
        product1 = inventory_grpc_client.create_product(
            name="Calc Product 1",
            price_per_unit=1250,
            count_in_stock=10
        )
        product2 = inventory_grpc_client.create_product(
            name="Calc Product 2",
            price_per_unit=3000,
            count_in_stock=10
        )
        
        # Add to cart
        cart_id = str(uuid.uuid4())
        cart_grpc_client.add_product_to_cart(cart_id, product1.id, 2)  # 2500
        cart_grpc_client.add_product_to_cart(cart_id, product2.id, 1)  # 3000
        
        # Create order
        order = order_grpc_client.create_order(cart_id=cart_id)
        
        # Verify calculations
        expected_total = (1250 * 2) + (3000 * 1)  # 5500
        assert order.total_amount == expected_total
