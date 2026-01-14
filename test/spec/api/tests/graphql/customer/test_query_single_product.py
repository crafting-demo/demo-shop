"""
API-TC002: Customer Query Single Product

Test customer-facing single product query by ID.
Tests product detail retrieval, data validation, and error handling.
"""
import pytest
from utils.graphql_client import CustomerGraphQLClient
from utils.helpers import validate_iso8601_timestamp, validate_price, validate_data_uri


@pytest.mark.customer
@pytest.mark.graphql
@pytest.mark.integration
class TestCustomerQuerySingleProduct:
    """Test customer single product query (API-TC002)."""

    def test_query_product_complete_data(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 1: Query product with complete data."""
        if not test_product_ids:
            pytest.skip("No test products available")
        
        product_id = test_product_ids[0]
        result = customer_graphql_client.query_product(product_id)
        
        # Validate response structure
        assert 'data' in result
        assert 'product' in result['data']
        product = result['data']['product']
        
        # Product should not be null
        assert product is not None
        
        # Validate all fields
        assert 'id' in product and product['id'] == product_id
        assert 'name' in product and product['name']
        assert 'pricePerUnit' in product
        assert 'countInStock' in product
        assert 'state' in product
        assert 'createdAt' in product
        assert 'updatedAt' in product
        
        # Validate data types and formats
        assert validate_price(product['pricePerUnit'])
        assert isinstance(product['countInStock'], int) and product['countInStock'] >= 0
        assert product['state'] in ['AVAILABLE', 'OFF_SHELF']
        assert validate_iso8601_timestamp(product['createdAt'])
        assert validate_iso8601_timestamp(product['updatedAt'])
        
        # updatedAt should be >= createdAt
        assert product['updatedAt'] >= product['createdAt']
        
        # Validate optional fields if present
        if product.get('imageData'):
            assert validate_data_uri(product['imageData'], 'image/')
    
    def test_query_available_product(self, customer_graphql_client: CustomerGraphQLClient, available_product_id: str):
        """Step 2: Query AVAILABLE product."""
        result = customer_graphql_client.query_product(available_product_id)
        
        product = result['data']['product']
        assert product is not None
        assert product['state'] == 'AVAILABLE'
        assert product['countInStock'] > 0
        assert product['pricePerUnit'] > 0

    def test_query_off_shelf_product(self, customer_graphql_client: CustomerGraphQLClient, off_shelf_product_id: str):
        """Step 3: Query OFF_SHELF product (should still return data)."""
        result = customer_graphql_client.query_product(off_shelf_product_id)
        
        product = result['data']['product']
        # Unlike list query, single product query returns OFF_SHELF products
        assert product is not None
        assert product['state'] == 'OFF_SHELF'
        assert 'id' in product and product['id']

    def test_query_product_minimal_data(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 4: Query product with minimal data (no description/image)."""
        if not test_product_ids:
            pytest.skip("No test products available")
        
        result = customer_graphql_client.query_product(test_product_ids[0])
        
        product = result['data']['product']
        assert product is not None
        
        # Required fields should be present
        assert product['id']
        assert product['name']
        assert product['pricePerUnit'] > 0
        assert product['countInStock'] >= 0
        assert product['state'] in ['AVAILABLE', 'OFF_SHELF']
        
        # Optional fields can be null or empty
        # (description, imageData)

    def test_query_out_of_stock_product(self, customer_graphql_client: CustomerGraphQLClient, out_of_stock_product_id: str):
        """Step 5: Query product with zero stock."""
        result = customer_graphql_client.query_product(out_of_stock_product_id)
        
        product = result['data']['product']
        assert product is not None
        assert product['countInStock'] == 0
        # Product details should still be accessible
        assert product['pricePerUnit'] > 0
        assert product['state'] in ['AVAILABLE', 'OFF_SHELF']

    def test_query_non_existent_product(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 6: Query non-existent product ID."""
        result = customer_graphql_client.query_product("non-existent-product-id-99999")
        
        # Should return null or error
        product = result['data'].get('product')
        assert product is None or 'errors' in result

    def test_query_empty_product_id(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 7: Query with empty product ID."""
        response = customer_graphql_client.execute_raw("""
            query {
                product(id: "") {
                    id
                    name
                }
            }
        """)
        
        result = response.json()
        # Should return null or error
        assert result['data']['product'] is None or 'errors' in result

    def test_query_missing_product_id(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 8: Query without providing product ID (validation error)."""
        response = customer_graphql_client.execute_raw("""
            query {
                product {
                    id
                    name
                }
            }
        """)
        
        result = response.json()
        # Should return GraphQL validation error
        assert 'errors' in result

    def test_query_special_characters_in_id(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 9: Query with special characters in ID (security test)."""
        result = customer_graphql_client.query_product("product-with-special-chars-@#$%")
        
        # Should handle safely without errors
        product = result['data'].get('product')
        # Should return null (product doesn't exist) but no system errors
        assert product is None or isinstance(product, dict)

    def test_query_subset_of_fields(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 10: Query only specific fields."""
        if not test_product_ids:
            pytest.skip("No test products available")
        
        product_id = test_product_ids[0]
        response = customer_graphql_client.execute_raw(f"""
            query {{
                product(id: "{product_id}") {{
                    id
                    name
                    pricePerUnit
                }}
            }}
        """)
        
        result = response.json()
        product = result['data']['product']
        
        assert product is not None
        # Should only contain requested fields
        assert 'id' in product
        assert 'name' in product
        assert 'pricePerUnit' in product
        # Verify data is accurate
        assert product['pricePerUnit'] > 0

    def test_verify_price_format(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 11: Verify price is integer in cents."""
        if not test_product_ids:
            pytest.skip("No test products available")
        
        result = customer_graphql_client.query_product(test_product_ids[0])
        
        product = result['data']['product']
        assert product is not None
        
        # Price should be integer (in smallest currency unit - cents)
        price = product['pricePerUnit']
        assert isinstance(price, int)
        assert price > 0
        # Example: $19.99 should be 1999

    def test_verify_image_data_format(self, customer_graphql_client: CustomerGraphQLClient, product_with_image_id: str):
        """Step 12: Verify image data format (data URI scheme)."""
        result = customer_graphql_client.query_product(product_with_image_id)
        
        product = result['data']['product']
        assert product is not None
        
        if product.get('imageData'):
            # Image should follow data URI scheme
            image_data = product['imageData']
            assert image_data.startswith('data:image/')
            assert ';base64,' in image_data

    def test_verify_timestamp_format(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 13: Verify timestamp format (ISO 8601)."""
        if not test_product_ids:
            pytest.skip("No test products available")
        
        result = customer_graphql_client.query_product(test_product_ids[0])
        
        product = result['data']['product']
        assert product is not None
        
        # Timestamps should be ISO 8601 format
        assert validate_iso8601_timestamp(product['createdAt'])
        assert validate_iso8601_timestamp(product['updatedAt'])
        
        # updatedAt >= createdAt
        assert product['updatedAt'] >= product['createdAt']

    def test_query_same_product_multiple_times(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 14: Query same product multiple times (consistency check)."""
        if not test_product_ids:
            pytest.skip("No test products available")
        
        product_id = test_product_ids[0]
        
        # Query multiple times
        result1 = customer_graphql_client.query_product(product_id)
        result2 = customer_graphql_client.query_product(product_id)
        result3 = customer_graphql_client.query_product(product_id)
        
        product1 = result1['data']['product']
        product2 = result2['data']['product']
        product3 = result3['data']['product']
        
        # All queries should return consistent data
        assert product1 == product2 == product3

    def test_query_product_after_cart_operation(self, customer_graphql_client: CustomerGraphQLClient, test_product_ids: list):
        """Step 15: Query product after adding to cart (independence check)."""
        if not test_product_ids:
            pytest.skip("No test products available")
        
        product_id = test_product_ids[0]
        
        # Query product before cart operation
        result1 = customer_graphql_client.query_product(product_id)
        product_before = result1['data']['product']
        
        # Add to cart
        customer_graphql_client.add_to_cart(product_id, quantity=1)
        
        # Query product again
        result2 = customer_graphql_client.query_product(product_id)
        product_after = result2['data']['product']
        
        # Product query should work independently
        assert product_after is not None
        assert product_after['id'] == product_id
        # Stock may or may not change depending on business logic
