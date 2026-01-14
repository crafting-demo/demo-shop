"""
API-TC006: Admin Product CRUD Operations

Test admin product creation, update, and deletion operations.
"""
import pytest
from utils.graphql_client import AdminGraphQLClient
from utils.helpers import generate_test_image_data, validate_iso8601_timestamp


@pytest.mark.admin
@pytest.mark.graphql
@pytest.mark.integration
class TestAdminProductCRUD:
    """Test admin product CRUD operations (API-TC006)."""

    def test_create_product_complete_data(self, admin_graphql_client: AdminGraphQLClient):
        """Step 1: Create product with complete data."""
        result = admin_graphql_client.create_product(
            name="Test Gaming Laptop",
            description="High-performance gaming laptop with RGB keyboard",
            image_data=generate_test_image_data(),
            price_per_unit=129999,
            count_in_stock=15,
            state="AVAILABLE"
        )
        
        product = result['data']['createProduct']
        
        # Validate all fields
        assert 'id' in product and product['id']
        assert product['name'] == "Test Gaming Laptop"
        assert product['description'] == "High-performance gaming laptop with RGB keyboard"
        assert product['imageData'].startswith('data:image/')
        assert product['pricePerUnit'] == 129999
        assert product['countInStock'] == 15
        assert product['state'] == 'AVAILABLE'
        assert validate_iso8601_timestamp(product['createdAt'])
        assert validate_iso8601_timestamp(product['updatedAt'])
        assert product['createdAt'] == product['updatedAt']  # Newly created
        
        # Save ID for later tests
        return product['id']

    def test_create_product_minimal_data(self, admin_graphql_client: AdminGraphQLClient):
        """Step 2: Create product with minimal required fields."""
        result = admin_graphql_client.create_product(
            name="Simple Product",
            price_per_unit=999,
            count_in_stock=10
        )
        
        product = result['data']['createProduct']
        
        assert product['name'] == "Simple Product"
        assert product['pricePerUnit'] == 999
        assert product['countInStock'] == 10
        # Default state should be AVAILABLE
        assert product['state'] == 'AVAILABLE'
        # Optional fields should be null or empty
        assert product['description'] is None or product['description'] == ''
        assert product['imageData'] is None or product['imageData'] == ''

    def test_create_product_off_shelf_state(self, admin_graphql_client: AdminGraphQLClient):
        """Step 3: Create product with OFF_SHELF state."""
        result = admin_graphql_client.create_product(
            name="Coming Soon Product",
            description="Product launching next month",
            price_per_unit=4999,
            count_in_stock=0,
            state="OFF_SHELF"
        )
        
        product = result['data']['createProduct']
        assert product['state'] == 'OFF_SHELF'
        assert product['countInStock'] == 0  # Zero stock is allowed

    def test_create_product_missing_name_fails(self, admin_graphql_client: AdminGraphQLClient):
        """Step 4: Create product without name (should fail)."""
        response = admin_graphql_client.execute_raw("""
            mutation {
                createProduct(input: {pricePerUnit: 1000, countInStock: 5}) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_create_product_empty_name_fails(self, admin_graphql_client: AdminGraphQLClient):
        """Step 5: Create product with empty name (should fail)."""
        response = admin_graphql_client.execute_raw("""
            mutation {
                createProduct(input: {name: "", pricePerUnit: 1000, countInStock: 5}) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_create_product_invalid_price_fails(self, admin_graphql_client: AdminGraphQLClient):
        """Step 6: Create product with zero/negative price (should fail)."""
        # Zero price
        response1 = admin_graphql_client.execute_raw("""
            mutation {
                createProduct(input: {name: "Invalid", pricePerUnit: 0, countInStock: 5}) {
                    id
                }
            }
        """)
        assert 'errors' in response1.json()
        
        # Negative price
        response2 = admin_graphql_client.execute_raw("""
            mutation {
                createProduct(input: {name: "Invalid", pricePerUnit: -100, countInStock: 5}) {
                    id
                }
            }
        """)
        assert 'errors' in response2.json()

    def test_update_product_name(self, admin_graphql_client: AdminGraphQLClient):
        """Step 8: Update product name."""
        # First create a product
        create_result = admin_graphql_client.create_product(
            name="Original Name",
            price_per_unit=1000,
            count_in_stock=10
        )
        product_id = create_result['data']['createProduct']['id']
        
        # Update name
        update_result = admin_graphql_client.update_product(
            product_id=product_id,
            name="Updated Name"
        )
        
        product = update_result['data']['updateProduct']
        assert product['name'] == "Updated Name"
        assert product['pricePerUnit'] == 1000  # Unchanged
        assert product['countInStock'] == 10  # Unchanged
        assert product['updatedAt'] > product['createdAt']

    def test_update_product_multiple_fields(self, admin_graphql_client: AdminGraphQLClient):
        """Step 12: Update multiple fields simultaneously."""
        # Create product
        create_result = admin_graphql_client.create_product(
            name="Multi Update Test",
            price_per_unit=1000,
            count_in_stock=10
        )
        product_id = create_result['data']['createProduct']['id']
        
        # Update multiple fields
        update_result = admin_graphql_client.update_product(
            product_id=product_id,
            name="Updated Multi",
            description="Now has description",
            price_per_unit=1299,
            count_in_stock=20
        )
        
        product = update_result['data']['updateProduct']
        assert product['name'] == "Updated Multi"
        assert product['description'] == "Now has description"
        assert product['pricePerUnit'] == 1299
        assert product['countInStock'] == 20

    def test_update_nonexistent_product_fails(self, admin_graphql_client: AdminGraphQLClient):
        """Step 13: Update non-existent product (should fail)."""
        response = admin_graphql_client.execute_raw("""
            mutation {
                updateProduct(input: {id: "non-existent-999", name: "Fail"}) {
                    id
                }
            }
        """)
        
        result = response.json()
        assert 'errors' in result

    def test_remove_product(self, admin_graphql_client: AdminGraphQLClient):
        """Step 20: Remove product (soft delete)."""
        # Create product
        create_result = admin_graphql_client.create_product(
            name="To Be Deleted",
            price_per_unit=1000,
            count_in_stock=5
        )
        product_id = create_result['data']['createProduct']['id']
        
        # Remove product
        remove_result = admin_graphql_client.remove_product(product_id)
        
        # Should return true
        assert remove_result['data']['removeProduct'] is True

    def test_remove_nonexistent_product(self, admin_graphql_client: AdminGraphQLClient):
        """Step 21: Remove non-existent product."""
        response = admin_graphql_client.execute_raw("""
            mutation {
                removeProduct(id: "non-existent-999")
            }
        """)
        
        result = response.json()
        # Should have error or return false
        if 'errors' not in result:
            assert result['data']['removeProduct'] is False

    def test_create_product_with_unicode(self, admin_graphql_client: AdminGraphQLClient):
        """Step 24: Create product with Unicode characters."""
        result = admin_graphql_client.create_product(
            name="Gaming Laptop ゲーミングノートPC 游戏笔记本",
            description="Международный продукт",
            price_per_unit=99999,
            count_in_stock=5
        )
        
        product = result['data']['createProduct']
        assert product['name'] == "Gaming Laptop ゲーミングノートPC 游戏笔记本"
        assert product['description'] == "Международный продукт"

    def test_update_product_set_stock_zero(self, admin_graphql_client: AdminGraphQLClient):
        """Step 26: Update product to set stock to zero."""
        # Create product
        create_result = admin_graphql_client.create_product(
            name="Zero Stock Test",
            price_per_unit=1000,
            count_in_stock=10
        )
        product_id = create_result['data']['createProduct']['id']
        
        # Set stock to zero
        update_result = admin_graphql_client.update_product(
            product_id=product_id,
            count_in_stock=0
        )
        
        product = update_result['data']['updateProduct']
        assert product['countInStock'] == 0
        # State should remain unchanged

    def test_create_and_verify_timestamps(self, admin_graphql_client: AdminGraphQLClient):
        """Test timestamps are properly set on create and update."""
        import time
        
        # Create product
        create_result = admin_graphql_client.create_product(
            name="Timestamp Test",
            price_per_unit=1000,
            count_in_stock=5
        )
        product = create_result['data']['createProduct']
        product_id = product['id']
        created_at = product['createdAt']
        updated_at1 = product['updatedAt']
        
        # createdAt should equal updatedAt on creation
        assert created_at == updated_at1
        
        # Wait a moment
        time.sleep(0.1)
        
        # Update product
        update_result = admin_graphql_client.update_product(
            product_id=product_id,
            name="Updated Timestamp"
        )
        updated_product = update_result['data']['updateProduct']
        
        # createdAt should not change
        assert updated_product['createdAt'] == created_at
        # updatedAt should be later
        assert updated_product['updatedAt'] > updated_at1
