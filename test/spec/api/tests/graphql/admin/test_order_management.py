"""
API-TC007: Admin Order Management Operations

Test admin order management including queries with filters and state updates.
Tests order lifecycle, state transitions, and business rule enforcement.
"""
import pytest
from utils.graphql_client import AdminGraphQLClient, CustomerGraphQLClient
from utils.helpers import validate_iso8601_timestamp


@pytest.mark.admin
@pytest.mark.graphql
@pytest.mark.integration
class TestAdminOrderManagement:
    """Test admin order management operations (API-TC007)."""

    def test_query_all_orders_no_filters(self, admin_graphql_client: AdminGraphQLClient):
        """Step 1: Query all orders without filters."""
        result = admin_graphql_client.query_orders()
        
        orders_data = result['data']['orders']
        edges = orders_data['edges']
        page_info = orders_data['pageInfo']
        
        # Should return orders (default 20 or fewer)
        assert len(edges) <= 20
        
        # Validate each order
        for edge in edges:
            node = edge['node']
            assert 'id' in node and node['id']
            assert 'customerName' in node
            assert 'customerEmail' in node
            assert 'shippingAddress' in node
            assert 'items' in node
            assert 'totalPrice' in node
            assert 'state' in node
            assert node['state'] in ['PROCESSING', 'SHIPPED', 'COMPLETED', 'CANCELED']
            assert 'createdAt' in node
            assert 'updatedAt' in node
            
        # Validate page info
        assert 'totalCount' in page_info
        assert isinstance(page_info['totalCount'], int)

    def test_filter_orders_by_processing_state(self, admin_graphql_client: AdminGraphQLClient):
        """Step 2: Filter orders by PROCESSING state."""
        result = admin_graphql_client.query_orders(first=50, state_filter='PROCESSING')
        
        edges = result['data']['orders']['edges']
        
        # All orders should be PROCESSING
        for edge in edges:
            assert edge['node']['state'] == 'PROCESSING'

    def test_filter_orders_by_shipped_state(self, admin_graphql_client: AdminGraphQLClient):
        """Step 3: Filter orders by SHIPPED state."""
        result = admin_graphql_client.query_orders(first=50, state_filter='SHIPPED')
        
        edges = result['data']['orders']['edges']
        
        # All orders should be SHIPPED
        for edge in edges:
            assert edge['node']['state'] == 'SHIPPED'

    def test_filter_orders_by_completed_state(self, admin_graphql_client: AdminGraphQLClient):
        """Step 4: Filter orders by COMPLETED state."""
        result = admin_graphql_client.query_orders(state_filter='COMPLETED')
        
        edges = result['data']['orders']['edges']
        
        # All orders should be COMPLETED
        for edge in edges:
            assert edge['node']['state'] == 'COMPLETED'

    def test_filter_orders_by_canceled_state(self, admin_graphql_client: AdminGraphQLClient):
        """Step 5: Filter orders by CANCELED state."""
        result = admin_graphql_client.query_orders(state_filter='CANCELED')
        
        edges = result['data']['orders']['edges']
        
        # All orders should be CANCELED
        for edge in edges:
            assert edge['node']['state'] == 'CANCELED'

    def test_filter_orders_by_email(self, admin_graphql_client: AdminGraphQLClient, test_order_email: str):
        """Step 6: Filter orders by customer email."""
        result = admin_graphql_client.query_orders(customer_email=test_order_email)
        
        edges = result['data']['orders']['edges']
        
        # All orders should match the email
        for edge in edges:
            assert edge['node']['customerEmail'] == test_order_email

    def test_ship_order_from_processing(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 7: Ship order (PROCESSING → SHIPPED)."""
        # Create a test order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Test Ship User",
            customer_email="ship@example.com",
            shipping_address="Ship Test St"
        )
        order_id = order_result['data']['placeOrder']['id']
        
        # Ship the order
        result = admin_graphql_client.ship_order(order_id)
        
        order = result['data']['shipOrder']
        assert order['state'] == 'SHIPPED'
        assert order['updatedAt'] > order['createdAt']

    def test_complete_order_from_shipped(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 8: Complete order (SHIPPED → COMPLETED)."""
        # Create and ship an order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Test Complete User",
            customer_email="complete@example.com",
            shipping_address="Complete Test St"
        )
        order_id = order_result['data']['placeOrder']['id']
        admin_graphql_client.ship_order(order_id)
        
        # Complete the order
        result = admin_graphql_client.complete_order(order_id)
        
        order = result['data']['completeOrder']
        assert order['state'] == 'COMPLETED'

    def test_cancel_order_from_processing(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 9: Cancel order (PROCESSING → CANCELED)."""
        # Create a test order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Test Cancel User",
            customer_email="cancel@example.com",
            shipping_address="Cancel Test St"
        )
        order_id = order_result['data']['placeOrder']['id']
        
        # Cancel the order
        result = admin_graphql_client.cancel_order(order_id)
        
        order = result['data']['cancelOrder']
        assert order['state'] == 'CANCELED'

    def test_cancel_order_from_shipped(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 10: Cancel order (SHIPPED → CANCELED)."""
        # Create and ship an order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Test Cancel Shipped",
            customer_email="cancelshipped@example.com",
            shipping_address="Cancel Shipped Test St"
        )
        order_id = order_result['data']['placeOrder']['id']
        admin_graphql_client.ship_order(order_id)
        
        # Cancel the shipped order
        result = admin_graphql_client.cancel_order(order_id)
        
        order = result['data']['cancelOrder']
        assert order['state'] == 'CANCELED'

    def test_invalid_transition_ship_completed(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 11: Invalid transition - ship completed order."""
        # Create, ship, and complete an order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Test Invalid Ship",
            customer_email="invalidship@example.com",
            shipping_address="Invalid Ship Test St"
        )
        order_id = order_result['data']['placeOrder']['id']
        admin_graphql_client.ship_order(order_id)
        admin_graphql_client.complete_order(order_id)
        
        # Try to ship completed order (should fail)
        response = admin_graphql_client.execute_raw(f"""
            mutation {{
                shipOrder(orderId: "{order_id}") {{
                    id
                    state
                }}
            }}
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_invalid_transition_complete_processing(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 12: Invalid transition - complete order from PROCESSING."""
        # Create an order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Test Invalid Complete",
            customer_email="invalidcomplete@example.com",
            shipping_address="Invalid Complete Test St"
        )
        order_id = order_result['data']['placeOrder']['id']
        
        # Try to complete without shipping first (should fail)
        response = admin_graphql_client.execute_raw(f"""
            mutation {{
                completeOrder(orderId: "{order_id}") {{
                    id
                    state
                }}
            }}
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_invalid_transition_cancel_completed(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 13: Invalid transition - cancel completed order."""
        # Create, ship, and complete an order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Test Invalid Cancel",
            customer_email="invalidcancel@example.com",
            shipping_address="Invalid Cancel Test St"
        )
        order_id = order_result['data']['placeOrder']['id']
        admin_graphql_client.ship_order(order_id)
        admin_graphql_client.complete_order(order_id)
        
        # Try to cancel completed order (should fail)
        response = admin_graphql_client.execute_raw(f"""
            mutation {{
                cancelOrder(orderId: "{order_id}") {{
                    id
                    state
                }}
            }}
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_update_non_existent_order(self, admin_graphql_client: AdminGraphQLClient):
        """Step 14: Update non-existent order."""
        response = admin_graphql_client.execute_raw("""
            mutation {
                shipOrder(orderId: "non-existent-order-id-99999") {
                    id
                    state
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_pagination_with_order_filters(self, admin_graphql_client: AdminGraphQLClient):
        """Step 15: Pagination with order filters."""
        # First page
        first_result = admin_graphql_client.query_orders(first=10, state_filter='PROCESSING')
        first_page_info = first_result['data']['orders']['pageInfo']
        
        if not first_page_info['hasNextPage']:
            pytest.skip("Not enough PROCESSING orders for pagination test")
        
        # Second page
        end_cursor = first_page_info['endCursor']
        second_result = admin_graphql_client.query_orders(
            first=10,
            after=end_cursor,
            state_filter='PROCESSING'
        )
        second_edges = second_result['data']['orders']['edges']
        
        # All orders on second page should still be PROCESSING
        for edge in second_edges:
            assert edge['node']['state'] == 'PROCESSING'

    def test_verify_order_data_immutability(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 16: Verify order data immutability after state changes."""
        # Create an order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=2)
        order_result = customer_graphql_client.place_order(
            customer_name="Immutability Test",
            customer_email="immutable@example.com",
            shipping_address="Immutable Test St"
        )
        order = order_result['data']['placeOrder']
        original_total = order['totalPrice']
        original_items = order['items']
        
        # Ship the order
        admin_graphql_client.ship_order(order['id'])
        
        # Query the order
        query_result = admin_graphql_client.query_order(order['id'])
        updated_order = query_result['data']['order']
        
        # Order data should remain immutable
        assert updated_order['totalPrice'] == original_total
        assert len(updated_order['items']) == len(original_items)
        assert updated_order['customerName'] == order['customerName']
        assert updated_order['customerEmail'] == order['customerEmail']
        assert updated_order['shippingAddress'] == order['shippingAddress']

    def test_verify_timestamp_updates(
        self, 
        admin_graphql_client: AdminGraphQLClient,
        customer_graphql_client: CustomerGraphQLClient,
        test_product_ids: list
    ):
        """Step 17: Verify timestamps update on state changes."""
        # Create an order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        order_result = customer_graphql_client.place_order(
            customer_name="Timestamp Test",
            customer_email="timestamp@example.com",
            shipping_address="Timestamp Test St"
        )
        order = order_result['data']['placeOrder']
        created_at = order['createdAt']
        
        # Ship the order
        ship_result = admin_graphql_client.ship_order(order['id'])
        shipped_order = ship_result['data']['shipOrder']
        
        # updatedAt should be greater than createdAt
        assert shipped_order['updatedAt'] > created_at
        assert validate_iso8601_timestamp(shipped_order['updatedAt'])
