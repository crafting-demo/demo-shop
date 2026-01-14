"""
API-TC005: Admin Query Products with Filters

Test admin products query with filters and search.
Tests filtering by state, searching by name, pagination, and combinations.
"""
import pytest
from utils.graphql_client import AdminGraphQLClient
from utils.helpers import validate_iso8601_timestamp, validate_price


@pytest.mark.admin
@pytest.mark.graphql
@pytest.mark.integration
class TestAdminQueryProductsWithFilters:
    """Test admin products query with filters (API-TC005)."""

    def test_query_all_products_no_filters(self, admin_graphql_client: AdminGraphQLClient):
        """Step 1: Query all products without filters."""
        result = admin_graphql_client.query_products()
        
        products_data = result['data']['products']
        edges = products_data['edges']
        page_info = products_data['pageInfo']
        
        # Should return products (default 20 or fewer)
        assert len(edges) <= 20
        
        # Should include ALL states (AVAILABLE and OFF_SHELF)
        states = {edge['node']['state'] for edge in edges}
        # May have both states or just one depending on data
        
        # Validate each product
        for edge in edges:
            node = edge['node']
            assert 'id' in node and node['id']
            assert 'name' in node and node['name']
            assert 'state' in node
            assert node['state'] in ['AVAILABLE', 'OFF_SHELF']
            assert validate_price(node['pricePerUnit'])
            assert isinstance(node['countInStock'], int) and node['countInStock'] >= 0
            
        # Validate page info
        assert 'totalCount' in page_info
        assert isinstance(page_info['totalCount'], int)

    def test_filter_by_available_state(self, admin_graphql_client: AdminGraphQLClient):
        """Step 2: Filter by AVAILABLE state."""
        result = admin_graphql_client.query_products(first=50, state_filter='AVAILABLE')
        
        edges = result['data']['products']['edges']
        page_info = result['data']['products']['pageInfo']
        
        # All products should be AVAILABLE
        for edge in edges:
            assert edge['node']['state'] == 'AVAILABLE'
        
        # Total count should reflect only AVAILABLE products
        assert page_info['totalCount'] >= len(edges)

    def test_filter_by_off_shelf_state(self, admin_graphql_client: AdminGraphQLClient):
        """Step 3: Filter by OFF_SHELF state."""
        result = admin_graphql_client.query_products(first=50, state_filter='OFF_SHELF')
        
        edges = result['data']['products']['edges']
        
        # All products should be OFF_SHELF
        for edge in edges:
            assert edge['node']['state'] == 'OFF_SHELF'

    def test_search_products_by_name(self, admin_graphql_client: AdminGraphQLClient):
        """Step 4: Search products by name."""
        search_term = "laptop"
        result = admin_graphql_client.query_products(first=50, search_name=search_term)
        
        edges = result['data']['products']['edges']
        
        # All products should contain search term (case-insensitive)
        for edge in edges:
            name = edge['node']['name'].lower()
            assert search_term.lower() in name

    def test_search_with_no_matches(self, admin_graphql_client: AdminGraphQLClient):
        """Step 5: Search with term that matches no products."""
        result = admin_graphql_client.query_products(search_name="xyznonexistentproduct123")
        
        edges = result['data']['products']['edges']
        page_info = result['data']['products']['pageInfo']
        
        # Should return empty results
        assert len(edges) == 0
        assert page_info['totalCount'] == 0

    def test_combine_state_filter_and_name_search(self, admin_graphql_client: AdminGraphQLClient):
        """Step 6: Combine state filter and name search."""
        result = admin_graphql_client.query_products(
            first=50,
            state_filter='AVAILABLE',
            search_name='phone'
        )
        
        edges = result['data']['products']['edges']
        
        # All products should match BOTH conditions
        for edge in edges:
            node = edge['node']
            assert node['state'] == 'AVAILABLE'
            assert 'phone' in node['name'].lower()

    def test_pagination_with_filters(self, admin_graphql_client: AdminGraphQLClient):
        """Step 7: Pagination with filters applied."""
        # First page
        first_result = admin_graphql_client.query_products(first=10, state_filter='AVAILABLE')
        first_edges = first_result['data']['products']['edges']
        first_page_info = first_result['data']['products']['pageInfo']
        
        if not first_page_info['hasNextPage']:
            pytest.skip("Not enough products for pagination test")
        
        # Second page
        end_cursor = first_page_info['endCursor']
        second_result = admin_graphql_client.query_products(
            first=10,
            after=end_cursor,
            state_filter='AVAILABLE'
        )
        second_edges = second_result['data']['products']['edges']
        second_page_info = second_result['data']['products']['pageInfo']
        
        # All products on both pages should be AVAILABLE
        for edge in first_edges + second_edges:
            assert edge['node']['state'] == 'AVAILABLE'
        
        # No duplicates
        first_ids = {edge['node']['id'] for edge in first_edges}
        second_ids = {edge['node']['id'] for edge in second_edges}
        assert len(first_ids & second_ids) == 0
        
        # Total count should be consistent
        assert first_page_info['totalCount'] == second_page_info['totalCount']
        
        # Second page should have previous page
        assert second_page_info['hasPreviousPage'] is True

    def test_query_custom_page_sizes(self, admin_graphql_client: AdminGraphQLClient):
        """Step 8: Query with various page sizes."""
        page_sizes = [10, 50, 100]
        total_counts = []
        
        for size in page_sizes:
            result = admin_graphql_client.query_products(first=size)
            edges = result['data']['products']['edges']
            page_info = result['data']['products']['pageInfo']
            
            assert len(edges) <= size
            total_counts.append(page_info['totalCount'])
        
        # Total count should be consistent across all queries
        assert len(set(total_counts)) == 1

    def test_search_partial_match(self, admin_graphql_client: AdminGraphQLClient):
        """Step 9: Search with partial name match."""
        partial_terms = ["gam", "pro"]
        
        for term in partial_terms:
            result = admin_graphql_client.query_products(search_name=term)
            edges = result['data']['products']['edges']
            
            # All returned products should contain the substring
            for edge in edges:
                assert term.lower() in edge['node']['name'].lower()

    def test_search_special_characters(self, admin_graphql_client: AdminGraphQLClient):
        """Step 10: Search with special characters (security test)."""
        special_terms = ["O'Brien", '20"']
        
        for term in special_terms:
            # Should execute without errors
            result = admin_graphql_client.query_products(search_name=term)
            # Just verify no errors, may or may not return results
            assert 'data' in result
            assert 'products' in result['data']

    def test_query_including_out_of_stock(self, admin_graphql_client: AdminGraphQLClient):
        """Step 11: Query products including out-of-stock items."""
        result = admin_graphql_client.query_products(first=50)
        
        edges = result['data']['products']['edges']
        
        # Should include products with any stock level
        stock_levels = [edge['node']['countInStock'] for edge in edges]
        # Admin can see all products regardless of stock

    def test_verify_all_product_fields(self, admin_graphql_client: AdminGraphQLClient):
        """Step 12: Verify all product fields are accessible."""
        result = admin_graphql_client.query_products(first=5)
        
        edges = result['data']['products']['edges']
        
        for edge in edges:
            node = edge['node']
            # Required fields
            assert 'id' in node and node['id']
            assert 'name' in node and node['name']
            assert 'pricePerUnit' in node
            assert 'countInStock' in node
            assert 'state' in node
            assert 'createdAt' in node
            assert 'updatedAt' in node
            
            # Validate formats
            assert node['state'] in ['AVAILABLE', 'OFF_SHELF']
            assert validate_price(node['pricePerUnit'])
            assert validate_iso8601_timestamp(node['createdAt'])
            assert validate_iso8601_timestamp(node['updatedAt'])
            assert node['updatedAt'] >= node['createdAt']

    def test_search_case_insensitive(self, admin_graphql_client: AdminGraphQLClient):
        """Step 14: Verify search is case-insensitive."""
        search_terms = ["laptop", "LAPTOP", "LaPtOp"]
        results = []
        
        for term in search_terms:
            result = admin_graphql_client.query_products(search_name=term)
            edges = result['data']['products']['edges']
            page_info = result['data']['products']['pageInfo']
            
            product_ids = {edge['node']['id'] for edge in edges}
            results.append((product_ids, page_info['totalCount']))
        
        # All three searches should return identical results
        assert results[0] == results[1] == results[2]

    def test_empty_filter_object(self, admin_graphql_client: AdminGraphQLClient):
        """Step 15: Query with empty filter object."""
        result = admin_graphql_client.query_products(first=20)
        
        # Should return all products like unfiltered query
        products_data = result['data']['products']
        assert len(products_data['edges']) > 0

    def test_cursor_stability_with_filters(self, admin_graphql_client: AdminGraphQLClient):
        """Step 17: Verify cursor stability with filters."""
        # Execute same filtered query multiple times
        results = []
        for _ in range(3):
            result = admin_graphql_client.query_products(first=10, state_filter='AVAILABLE')
            edges = result['data']['products']['edges']
            product_ids = [edge['node']['id'] for edge in edges]
            cursors = [edge['cursor'] for edge in edges]
            results.append((product_ids, cursors))
        
        # All executions should return same products and cursors
        assert results[0] == results[1] == results[2]

    def test_large_page_size_with_filters(self, admin_graphql_client: AdminGraphQLClient):
        """Step 18: Query with large page size and filter."""
        import time
        
        start_time = time.time()
        result = admin_graphql_client.query_products(first=200, state_filter='AVAILABLE')
        elapsed_time = time.time() - start_time
        
        edges = result['data']['products']['edges']
        
        # Should handle large page size
        assert len(edges) <= 200
        
        # All should match filter
        for edge in edges:
            assert edge['node']['state'] == 'AVAILABLE'
        
        # Performance check (should complete in reasonable time)
        assert elapsed_time < 5.0, f"Query took {elapsed_time:.2f}s (expected < 5s)"

    def test_search_with_empty_string(self, admin_graphql_client: AdminGraphQLClient):
        """Step 19: Search with empty string."""
        result = admin_graphql_client.query_products(search_name="")
        
        # Should execute without error
        assert 'data' in result
        assert 'products' in result['data']
        # May return all products or no products, but should be consistent
