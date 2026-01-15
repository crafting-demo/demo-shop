"""
API-TC003: Customer Cart Operations

Test customer cart operations including add, update, remove, and clear.
"""
import pytest
from utils.graphql_client import CustomerGraphQLClient
from utils.helpers import calculate_cart_total


@pytest.mark.customer
@pytest.mark.graphql
@pytest.mark.integration
class TestCustomerCartOperations:
    """Test customer cart operations (API-TC003)."""

    def test_cart_auto_creation(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 1: Query cart before any operations (auto-creation)."""
        result = customer_graphql_client.query_cart()
        
        cart = result['data']['cart']
        assert 'id' in cart and cart['id']
        assert 'items' in cart
        assert len(cart['items']) == 0
        assert cart['totalPrice'] == 0

    def test_add_first_product(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 2: Add first product to cart."""
        # Clear cart first
        customer_graphql_client.clear_cart()
        
        # Add product
        product_id = test_product_ids[0]
        result = customer_graphql_client.add_to_cart(product_id, quantity=1)
        
        cart = result['data']['addToCart']
        assert len(cart['items']) == 1
        assert cart['items'][0]['product']['id'] == product_id
        assert cart['items'][0]['quantity'] == 1
        
        # Verify total price calculation
        item = cart['items'][0]
        expected_total = item['product']['pricePerUnit'] * item['quantity']
        assert item['totalPrice'] == expected_total
        assert cart['totalPrice'] == expected_total

    def test_add_same_product_increments(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 3: Add same product again (should increment quantity)."""
        # Clear and add first time
        customer_graphql_client.clear_cart()
        product_id = test_product_ids[0]
        customer_graphql_client.add_to_cart(product_id, quantity=1)
        
        # Add same product again
        result = customer_graphql_client.add_to_cart(product_id, quantity=2)
        
        cart = result['data']['addToCart']
        # Should still have one item (not duplicated)
        assert len(cart['items']) == 1
        # Quantity should be incremented (1 + 2 = 3)
        assert cart['items'][0]['quantity'] == 3

    def test_add_different_product(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 4: Add different product to cart."""
        # Clear and add first product
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=2)
        
        # Add second product
        result = customer_graphql_client.add_to_cart(test_product_ids[1], quantity=3)
        
        cart = result['data']['addToCart']
        assert len(cart['items']) == 2
        
        # Verify both products present
        product_ids = {item['product']['id'] for item in cart['items']}
        assert test_product_ids[0] in product_ids
        assert test_product_ids[1] in product_ids
        
        # Verify total price
        calculated_total = calculate_cart_total(cart['items'])
        assert cart['totalPrice'] == calculated_total

    def test_update_item_increase_quantity(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 5: Update item quantity (increase)."""
        # Setup: cart with one item
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=2)
        
        # Update to higher quantity
        result = customer_graphql_client.update_cart_item(test_product_ids[0], quantity=5)
        
        cart = result['data']['updateCartItem']
        assert len(cart['items']) == 1
        # Quantity should be set to exact value, not incremented
        assert cart['items'][0]['quantity'] == 5

    def test_update_item_decrease_quantity(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 6: Update item quantity (decrease)."""
        # Setup: cart with one item with high quantity
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=5)
        
        # Decrease quantity
        result = customer_graphql_client.update_cart_item(test_product_ids[0], quantity=2)
        
        cart = result['data']['updateCartItem']
        assert cart['items'][0]['quantity'] == 2

    def test_update_item_zero_removes(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 7: Update item quantity to zero (removes item)."""
        # Setup: cart with two items
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=5)
        customer_graphql_client.add_to_cart(test_product_ids[1], quantity=3)
        
        # Set first product quantity to zero
        result = customer_graphql_client.update_cart_item(test_product_ids[0], quantity=0)
        
        cart = result['data']['updateCartItem']
        # Should only have one item now
        assert len(cart['items']) == 1
        assert cart['items'][0]['product']['id'] == test_product_ids[1]

    def test_remove_item_from_cart(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 8: Remove item from cart."""
        # Setup: cart with two items
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=2)
        customer_graphql_client.add_to_cart(test_product_ids[1], quantity=3)
        
        # Remove first item
        result = customer_graphql_client.remove_from_cart(test_product_ids[0])
        
        cart = result['data']['removeFromCart']
        assert len(cart['items']) == 1
        assert cart['items'][0]['product']['id'] == test_product_ids[1]

    def test_clear_cart(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 10: Clear entire cart."""
        # Setup: cart with multiple items
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=1)
        customer_graphql_client.add_to_cart(test_product_ids[1], quantity=2)
        customer_graphql_client.add_to_cart(test_product_ids[2], quantity=3)
        
        # Clear cart
        result = customer_graphql_client.clear_cart()
        
        cart = result['data']['clearCart']
        assert len(cart['items']) == 0
        assert cart['totalPrice'] == 0

    def test_add_with_default_quantity(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 11: Add product without specifying quantity (default to 1)."""
        customer_graphql_client.clear_cart()
        
        # Add without quantity parameter
        result = customer_graphql_client.add_to_cart(test_product_ids[0])
        
        cart = result['data']['addToCart']
        assert len(cart['items']) == 1
        assert cart['items'][0]['quantity'] == 1

    def test_add_nonexistent_product_fails(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 13: Add non-existent product (should fail)."""
        customer_graphql_client.clear_cart()
        
        response = customer_graphql_client.execute_raw("""
            mutation {
                addToCart(input: {productId: "non-existent-999", quantity: 1}) {
                    id
                }
            }
        """)
        
        result = response.json()
        # Should have error
        assert 'errors' in result
        assert len(result['errors']) > 0

    def test_add_zero_quantity_fails(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 14: Add product with zero quantity (should fail)."""
        response = customer_graphql_client.execute_raw(f"""
            mutation {{
                addToCart(input: {{productId: "{test_product_ids[0]}", quantity: 0}}) {{
                    id
                }}
            }}
        """)
        
        result = response.json()
        # Should have error
        assert 'errors' in result

    def test_add_negative_quantity_fails(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 15: Add product with negative quantity (should fail)."""
        response = customer_graphql_client.execute_raw(f"""
            mutation {{
                addToCart(input: {{productId: "{test_product_ids[0]}", quantity: -5}}) {{
                    id
                }}
            }}
        """)
        
        result = response.json()
        # Should have error
        assert 'errors' in result

    def test_cart_persistence_across_queries(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 18: Verify cart persists across queries."""
        # Add items to cart
        customer_graphql_client.clear_cart()
        customer_graphql_client.add_to_cart(test_product_ids[0], quantity=3)
        customer_graphql_client.add_to_cart(test_product_ids[1], quantity=5)
        
        # Query cart multiple times
        result1 = customer_graphql_client.query_cart()
        result2 = customer_graphql_client.query_cart()
        result3 = customer_graphql_client.query_cart()
        
        cart1 = result1['data']['cart']
        cart2 = result2['data']['cart']
        cart3 = result3['data']['cart']
        
        # Cart ID should be consistent
        assert cart1['id'] == cart2['id'] == cart3['id']
        
        # Items should be consistent
        assert len(cart1['items']) == len(cart2['items']) == len(cart3['items']) == 2
        assert cart1['totalPrice'] == cart2['totalPrice'] == cart3['totalPrice']

    def test_price_calculation_accuracy(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 19: Verify price calculation accuracy."""
        # Setup cart with known quantities
        customer_graphql_client.clear_cart()
        result1 = customer_graphql_client.add_to_cart(test_product_ids[0], quantity=2)
        result2 = customer_graphql_client.add_to_cart(test_product_ids[1], quantity=2)
        result3 = customer_graphql_client.add_to_cart(test_product_ids[2], quantity=3)
        
        # Query final cart
        final_result = customer_graphql_client.query_cart()
        cart = final_result['data']['cart']
        
        # Verify each item total
        for item in cart['items']:
            expected_item_total = item['product']['pricePerUnit'] * item['quantity']
            assert item['totalPrice'] == expected_item_total
        
        # Verify cart total
        calculated_total = calculate_cart_total(cart['items'])
        assert cart['totalPrice'] == calculated_total
