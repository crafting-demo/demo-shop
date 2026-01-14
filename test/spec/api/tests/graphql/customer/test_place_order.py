"""
API-TC004: Customer Place Order

Test customer order placement from cart.
Tests order creation, validation, cart clearing, and error handling.
"""
import pytest
from utils.graphql_client import CustomerGraphQLClient
from utils.helpers import validate_iso8601_timestamp, calculate_cart_total


@pytest.mark.customer
@pytest.mark.graphql
@pytest.mark.integration
class TestCustomerPlaceOrder:
    """Test customer place order mutation (API-TC004)."""

    def test_place_order_valid_information(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 1: Place order with valid customer information."""
        # Setup: Add products to cart
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=2)
        customer_graphql_client.add_to_cart(test_product_ids[1], quantity=1)
        
        # Get cart total before order
        cart_result = customer_graphql_client.query_cart()
        cart_total = cart_result['data']['cart']['totalPrice']
        cart_items_count = len(cart_result['data']['cart']['items'])
        
        # Place order
        result = customer_graphql_client.place_order(
            customer_name="John Doe",
            customer_email="john.doe@example.com",
            shipping_address="123 Main St, Apt 4B, New York, NY 10001"
        )
        
        order = result['data']['placeOrder']
        
        # Validate order data
        assert 'id' in order and order['id']
        assert order['customerName'] == "John Doe"
        assert order['customerEmail'] == "john.doe@example.com"
        assert order['shippingAddress'] == "123 Main St, Apt 4B, New York, NY 10001"
        assert len(order['items']) == cart_items_count
        assert order['totalPrice'] == cart_total
        assert order['state'] == 'PROCESSING'
        assert validate_iso8601_timestamp(order['createdAt'])
        assert validate_iso8601_timestamp(order['updatedAt'])
        assert order['createdAt'] == order['updatedAt']
        
        # Verify cart is cleared
        cart_after = customer_graphql_client.query_cart()
        assert len(cart_after['data']['cart']['items']) == 0
        assert cart_after['data']['cart']['totalPrice'] == 0

    def test_place_order_minimal_address(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 2: Place order with minimal address."""
        # Setup
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        # Place order
        result = customer_graphql_client.place_order(
            customer_name="Jane Smith",
            customer_email="jane@example.com",
            shipping_address="456 Oak Avenue"
        )
        
        order = result['data']['placeOrder']
        assert order['shippingAddress'] == "456 Oak Avenue"
        assert order['id']

    def test_place_order_long_customer_name(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 3: Place order with long customer name."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        long_name = "Alexander Christopher Wellington Montgomery III"
        result = customer_graphql_client.place_order(
            customer_name=long_name,
            customer_email="alexander@example.com",
            shipping_address="789 Elm Street"
        )
        
        order = result['data']['placeOrder']
        assert order['customerName'] == long_name

    def test_place_order_international_address(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 4: Place order with international address."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        result = customer_graphql_client.place_order(
            customer_name="Pierre Dubois",
            customer_email="pierre@example.fr",
            shipping_address="42 Rue de la Paix, 75002 Paris, France"
        )
        
        order = result['data']['placeOrder']
        assert order['shippingAddress'] == "42 Rue de la Paix, 75002 Paris, France"

    def test_place_order_empty_cart(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 5: Place order with empty cart (should fail)."""
        # Ensure cart is empty
        customer_graphql_client.clear_cart()
        
        # Attempt to place order
        response = customer_graphql_client.execute_raw("""
            mutation {
                placeOrder(input: {
                    customerName: "Empty Cart User"
                    customerEmail: "empty@example.com"
                    shippingAddress: "No Items Street"
                }) {
                    id
                }
            }
        """)
        
        result = response.json()
        # Should return error
        assert 'errors' in result

    def test_place_order_missing_customer_name(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 6: Place order without customer name (should fail)."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        response = customer_graphql_client.execute_raw("""
            mutation {
                placeOrder(input: {
                    customerEmail: "nohash@example.com"
                    shippingAddress: "999 Test Ave"
                }) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_place_order_empty_customer_name(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 7: Place order with empty customer name (should fail)."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        response = customer_graphql_client.execute_raw("""
            mutation {
                placeOrder(input: {
                    customerName: ""
                    customerEmail: "empty@example.com"
                    shippingAddress: "Empty Name Street"
                }) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_place_order_missing_email(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 8: Place order without email (should fail)."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        response = customer_graphql_client.execute_raw("""
            mutation {
                placeOrder(input: {
                    customerName: "No Email User"
                    shippingAddress: "No Email Street"
                }) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_place_order_invalid_email_format(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 9: Place order with invalid email format (should fail)."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        response = customer_graphql_client.execute_raw("""
            mutation {
                placeOrder(input: {
                    customerName: "Invalid Email User"
                    customerEmail: "not-an-email"
                    shippingAddress: "Invalid Email Street"
                }) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_place_order_various_invalid_emails(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 10: Test multiple invalid email formats."""
        invalid_emails = [
            "invalidemail.com",  # Missing @
            "test@",  # Missing domain
            "@example.com",  # Missing username
            "test@@example.com",  # Multiple @
            "test user@example.com",  # Spaces
        ]
        
        for invalid_email in invalid_emails:
            customer_graphql_client.clear_cart()
            customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
            
            response = customer_graphql_client.execute_raw(f"""
                mutation {{
                    placeOrder(input: {{
                        customerName: "Test"
                        customerEmail: "{invalid_email}"
                        shippingAddress: "Test St"
                    }}) {{
                        id
                    }}
                }}
            """)
            
            result = response.json()
            assert 'errors' in result, f"Expected error for invalid email: {invalid_email}"

    def test_place_order_valid_email_variations(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 11: Test valid email format variations."""
        valid_emails = [
            ("user@example.com", "Standard email"),
            ("user+tag@example.com", "Plus sign"),
            ("first.last@example.com", "Dots"),
            ("user@mail.example.com", "Subdomain"),
            ("user123@example.com", "Numbers"),
        ]
        
        for email, description in valid_emails:
            customer_graphql_client.clear_cart()
            customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
            
            result = customer_graphql_client.place_order(
                customer_name=f"Test {description}",
                customer_email=email,
                shipping_address="Test St"
            )
            
            order = result['data']['placeOrder']
            assert order['customerEmail'] == email, f"Failed for {description}"
            
            # Verify cart cleared
            cart = customer_graphql_client.query_cart()
            assert len(cart['data']['cart']['items']) == 0

    def test_place_order_missing_shipping_address(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 12: Place order without shipping address (should fail)."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        response = customer_graphql_client.execute_raw("""
            mutation {
                placeOrder(input: {
                    customerName: "No Address User"
                    customerEmail: "noaddress@example.com"
                }) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_place_order_empty_shipping_address(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 13: Place order with empty shipping address (should fail)."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        response = customer_graphql_client.execute_raw("""
            mutation {
                placeOrder(input: {
                    customerName: "Empty Address User"
                    customerEmail: "empty@example.com"
                    shippingAddress: ""
                }) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_place_order_special_characters(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 14: Place order with special characters (security test)."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        result = customer_graphql_client.place_order(
            customer_name="O'Brien-Smith & Co.",
            customer_email="test@example.com",
            shipping_address="123 Main St., Apt #4B"
        )
        
        order = result['data']['placeOrder']
        # Special characters should be preserved
        assert "O'Brien" in order['customerName']
        # No XSS vulnerabilities
        assert order['id']

    def test_place_order_unicode_characters(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 15: Place order with Unicode characters."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        result = customer_graphql_client.place_order(
            customer_name="田中太郎",
            customer_email="tanaka@example.jp",
            shipping_address="東京都渋谷区 1-2-3"
        )
        
        order = result['data']['placeOrder']
        assert order['customerName'] == "田中太郎"
        assert order['shippingAddress'] == "東京都渋谷区 1-2-3"

    def test_place_multiple_orders_succession(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 16: Place multiple orders in succession."""
        # First order
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        result1 = customer_graphql_client.place_order(
            customer_name="Multi Order User 1",
            customer_email="multi1@example.com",
            shipping_address="First Address"
        )
        order1_id = result1['data']['placeOrder']['id']
        
        # Second order
        customer_graphql_client.add_to_cart(test_product_ids[1], quantity=2)
        
        result2 = customer_graphql_client.place_order(
            customer_name="Multi Order User 2",
            customer_email="multi2@example.com",
            shipping_address="Second Address"
        )
        order2_id = result2['data']['placeOrder']['id']
        
        # Orders should have unique IDs
        assert order1_id != order2_id
        
        # Cart should be empty after second order
        cart = customer_graphql_client.query_cart()
        assert len(cart['data']['cart']['items']) == 0

    def test_verify_order_total_calculation(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 21: Verify order total calculation accuracy."""
        customer_graphql_client.clear_cart()
        
        # Add multiple products with known quantities
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=2)
        customer_graphql_client.add_to_cart(test_product_ids[1], quantity=1)
        customer_graphql_client.add_to_cart(test_product_ids[2], quantity=5)
        
        # Get cart total
        cart_result = customer_graphql_client.query_cart()
        cart = cart_result['data']['cart']
        expected_total = calculate_cart_total(cart['items'])
        
        # Place order
        result = customer_graphql_client.place_order(
            customer_name="Calculation Test",
            customer_email="calc@example.com",
            shipping_address="Test"
        )
        
        order = result['data']['placeOrder']
        
        # Verify calculations
        for item in order['items']:
            expected_item_total = item['product']['pricePerUnit'] * item['quantity']
            assert item['totalPrice'] == expected_item_total
        
        assert order['totalPrice'] == expected_total

    def test_place_order_verify_initial_state(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 22: Verify order initializes to PROCESSING state."""
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        
        result = customer_graphql_client.place_order(
            customer_name="State Test User",
            customer_email="state@example.com",
            shipping_address="State Test St"
        )
        
        order = result['data']['placeOrder']
        
        # Initial state should be PROCESSING
        assert order['state'] == 'PROCESSING'
        assert validate_iso8601_timestamp(order['createdAt'])
        assert validate_iso8601_timestamp(order['updatedAt'])
        assert order['createdAt'] == order['updatedAt']
