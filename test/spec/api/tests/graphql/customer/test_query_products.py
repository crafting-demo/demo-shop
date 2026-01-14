"""
API-TC001: Customer Query Products

Test customer-facing products query with pagination.
Tests products listing, filtering (AVAILABLE only), pagination, and data validation.
"""
import pytest
from utils.graphql_client import CustomerGraphQLClient
from utils.helpers import validate_iso8601_timestamp, validate_price, validate_data_uri


@pytest.mark.customer
@pytest.mark.graphql
@pytest.mark.integration
class TestCustomerQueryProducts:
    """Test customer products query (API-TC001)."""

    def test_query_first_page_default(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 1: Query first page of products with default pagination."""
        result = customer_graphql_client.query_products()
        
        # Validate response structure
        assert 'data' in result
        assert 'products' in result['data']
        products_data = result['data']['products']
        
        # Validate edges
        assert 'edges' in products_data
        assert 'pageInfo' in products_data
        edges = products_data['edges']
        page_info = products_data['pageInfo']
        
        # Default page size is 20
        assert len(edges) <= 20
        
        # Validate each product
        for edge in edges:
            node = edge['node']
            assert 'id' in node and node['id']
            assert 'name' in node and node['name']
            assert 'pricePerUnit' in node
            assert 'countInStock' in node
            assert 'state' in node
            assert 'createdAt' in node
            assert 'updatedAt' in node
            
            # Customer query should only return AVAILABLE products
            assert node['state'] == 'AVAILABLE'
            # Should only show products with stock
            assert node['countInStock'] > 0
            # Price should be positive
            assert validate_price(node['pricePerUnit'])
            # Timestamps should be valid
            assert validate_iso8601_timestamp(node['createdAt'])
            assert validate_iso8601_timestamp(node['updatedAt'])
            
            # Validate image data if present
            if node.get('imageData'):
                assert validate_data_uri(node['imageData'], 'image/')
        
        # Validate page info
        assert 'hasNextPage' in page_info
        assert 'hasPreviousPage' in page_info
        assert 'totalCount' in page_info
        assert page_info['hasPreviousPage'] is False
        assert isinstance(page_info['totalCount'], int)
        assert page_info['totalCount'] > 0

    def test_query_custom_page_size(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 2: Query with custom page size."""
        result = customer_graphql_client.query_products(first=10)
        
        edges = result['data']['products']['edges']
        page_info = result['data']['products']['pageInfo']
        
        # Should return exactly 10 or fewer products
        assert len(edges) <= 10
        
        # All should be AVAILABLE
        for edge in edges:
            assert edge['node']['state'] == 'AVAILABLE'
        
        # Total count should be consistent
        assert page_info['totalCount'] > 0

    def test_query_second_page_with_cursor(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 3: Query second page using cursor."""
        # Get first page
        first_result = customer_graphql_client.query_products(first=10)
        first_edges = first_result['data']['products']['edges']
        first_page_info = first_result['data']['products']['pageInfo']
        
        # Skip if no next page
        if not first_page_info['hasNextPage']:
            pytest.skip("Not enough products for pagination test")
        
        # Get second page
        end_cursor = first_page_info['endCursor']
        second_result = customer_graphql_client.query_products(first=10, after=end_cursor)
        second_edges = second_result['data']['products']['edges']
        second_page_info = second_result['data']['products']['pageInfo']
        
        # Should have results
        assert len(second_edges) > 0
        assert len(second_edges) <= 10
        
        # No duplicate products
        first_ids = {edge['node']['id'] for edge in first_edges}
        second_ids = {edge['node']['id'] for edge in second_edges}
        assert len(first_ids & second_ids) == 0
        
        # Page info should indicate previous page exists
        assert second_page_info['hasPreviousPage'] is True
        
        # Total count should be consistent
        assert first_page_info['totalCount'] == second_page_info['totalCount']

    def test_query_large_page_size(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 4: Query with large page size."""
        result = customer_graphql_client.query_products(first=100)
        
        edges = result['data']['products']['edges']
        page_info = result['data']['products']['pageInfo']
        
        # Should return up to 100 products
        assert len(edges) <= 100
        
        # If total count > 100, should have next page
        if page_info['totalCount'] > 100:
            assert page_info['hasNextPage'] is True
        else:
            # Otherwise, should have returned all products
            assert len(edges) == page_info['totalCount']
            assert page_info['hasNextPage'] is False

    def test_query_zero_page_size(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 5: Query with zero page size (invalid)."""
        # This should either return error or empty results
        response = customer_graphql_client.execute_raw("""
            query {
                products(first: 0) {
                    edges {
                        node { id }
                    }
                }
            }
        """)
        
        result = response.json()
        
        # Should have error or return empty
        if 'errors' in result:
            # Expected error case
            assert len(result['errors']) > 0
        else:
            # Or returns empty edges
            edges = result['data']['products']['edges']
            assert len(edges) == 0

    def test_query_last_page(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 6: Query last page (end of results)."""
        # Navigate to last page
        cursor = None
        total_products = []
        max_iterations = 10  # Safety limit
        
        for _ in range(max_iterations):
            result = customer_graphql_client.query_products(first=20, after=cursor)
            edges = result['data']['products']['edges']
            page_info = result['data']['products']['pageInfo']
            
            total_products.extend([edge['node']['id'] for edge in edges])
            
            if not page_info['hasNextPage']:
                # Reached last page
                assert page_info['hasPreviousPage'] is True
                assert len(edges) <= 20
                break
            
            cursor = page_info['endCursor']
        else:
            pytest.skip("Too many products for pagination test")

    def test_off_shelf_products_excluded(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 7: Verify OFF_SHELF products are excluded."""
        # Query multiple pages
        result = customer_graphql_client.query_products(first=100)
        edges = result['data']['products']['edges']
        
        # All products should be AVAILABLE
        for edge in edges:
            assert edge['node']['state'] == 'AVAILABLE'
            assert edge['node']['state'] != 'OFF_SHELF'

    def test_out_of_stock_products_excluded(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 8: Verify out-of-stock products are excluded."""
        result = customer_graphql_client.query_products(first=100)
        edges = result['data']['products']['edges']
        
        # All products should have stock
        for edge in edges:
            assert edge['node']['countInStock'] > 0

    def test_product_field_data_integrity(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 9: Verify product field data integrity."""
        result = customer_graphql_client.query_products(first=5)
        edges = result['data']['products']['edges']
        
        assert len(edges) > 0
        
        for edge in edges:
            node = edge['node']
            
            # Required fields
            assert isinstance(node['id'], str) and node['id']
            assert isinstance(node['name'], str) and node['name']
            assert isinstance(node['pricePerUnit'], int) and node['pricePerUnit'] > 0
            assert isinstance(node['countInStock'], int) and node['countInStock'] >= 1
            assert node['state'] == 'AVAILABLE'
            
            # Timestamps
            assert validate_iso8601_timestamp(node['createdAt'])
            assert validate_iso8601_timestamp(node['updatedAt'])
            # updatedAt >= createdAt (allowing for same value)
            assert node['updatedAt'] >= node['createdAt']
            
            # Optional fields can be null or valid
            if node.get('description'):
                assert isinstance(node['description'], str)
            
            if node.get('imageData'):
                assert node['imageData'].startswith('data:image/')

    def test_cursor_consistency(self, customer_graphql_client: CustomerGraphQLClient):
        """Step 10: Verify cursor consistency across repeated queries."""
        # Query same page multiple times
        result1 = customer_graphql_client.query_products(first=10)
        result2 = customer_graphql_client.query_products(first=10)
        
        edges1 = result1['data']['products']['edges']
        edges2 = result2['data']['products']['edges']
        
        # Should return identical results
        ids1 = [edge['node']['id'] for edge in edges1]
        ids2 = [edge['node']['id'] for edge in edges2]
        assert ids1 == ids2
        
        # Cursors should match
        cursors1 = [edge['cursor'] for edge in edges1]
        cursors2 = [edge['cursor'] for edge in edges2]
        assert cursors1 == cursors2
        
        # Total count should be same
        assert result1['data']['products']['pageInfo']['totalCount'] == \
               result2['data']['products']['pageInfo']['totalCount']

    def test_all_cursors_unique(self, customer_graphql_client: CustomerGraphQLClient):
        """Test that all product cursors are unique."""
        result = customer_graphql_client.query_products(first=20)
        edges = result['data']['products']['edges']
        
        cursors = [edge['cursor'] for edge in edges]
        # All cursors should be unique
        assert len(cursors) == len(set(cursors))

    def test_deterministic_ordering(self, customer_graphql_client: CustomerGraphQLClient):
        """Test that products are returned in deterministic order."""
        # Query multiple times and verify order is consistent
        results = []
        for _ in range(3):
            result = customer_graphql_client.query_products(first=10)
            ids = [edge['node']['id'] for edge in result['data']['products']['edges']]
            results.append(ids)
        
        # All queries should return same order
        assert results[0] == results[1] == results[2]
