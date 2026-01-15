"""
API-TC008: gRPC InventoryService API

Test gRPC InventoryService operations.
Tests QueryProducts, GetProduct, CreateProduct, UpdateProduct, DeleteProduct.
"""
import pytest
from utils.grpc_client import InventoryServiceClient
from utils.helpers import validate_grpc_timestamp


@pytest.mark.grpc
@pytest.mark.integration
class TestGRPCInventoryService:
    """Test gRPC InventoryService (API-TC008)."""

    def test_query_products_all_no_filter(self, inventory_grpc_client: InventoryServiceClient):
        """Step 1: QueryProducts - all products without filter."""
        response = inventory_grpc_client.query_products(first=20)
        
        # Validate response structure
        assert hasattr(response, 'products')
        assert hasattr(response, 'page_info')
        assert hasattr(response, 'total_count')
        
        # Validate products
        assert len(response.products) <= 20
        
        for product in response.products:
            assert product.id
            assert product.name
            assert product.price_per_unit > 0
            assert product.count_in_stock >= 0
            assert product.state in [1, 2]  # AVAILABLE=1, OFF_SHELF=2
            assert hasattr(product, 'created_at')
            assert hasattr(product, 'updated_at')

    def test_query_products_filter_available(self, inventory_grpc_client: InventoryServiceClient):
        """Step 2: QueryProducts - filter by AVAILABLE state."""
        response = inventory_grpc_client.query_products(first=50, state_filter=1)  # AVAILABLE=1
        
        # All products should be AVAILABLE
        for product in response.products:
            assert product.state == 1

    def test_query_products_filter_off_shelf(self, inventory_grpc_client: InventoryServiceClient):
        """Step 3: QueryProducts - filter by OFF_SHELF state."""
        response = inventory_grpc_client.query_products(first=50, state_filter=2)  # OFF_SHELF=2
        
        # All products should be OFF_SHELF
        for product in response.products:
            assert product.state == 2

    def test_get_product_by_id(self, inventory_grpc_client: InventoryServiceClient, test_product_id: str):
        """Step 4: GetProduct - retrieve single product by ID."""
        product = inventory_grpc_client.get_product(test_product_id)
        
        assert product.id == test_product_id
        assert product.name
        assert product.price_per_unit > 0
        assert product.count_in_stock >= 0
        assert product.state in [1, 2]

    def test_get_product_not_found(self, inventory_grpc_client: InventoryServiceClient):
        """Step 5: GetProduct - non-existent product."""
        with pytest.raises(Exception) as exc_info:
            inventory_grpc_client.get_product("non-existent-product-id-99999")
        
        # Should return NOT_FOUND error
        assert "NOT_FOUND" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_create_product_complete_data(self, inventory_grpc_client: InventoryServiceClient):
        """Step 6: CreateProduct - with complete data."""
        product = inventory_grpc_client.create_product(
            name="gRPC Test Gaming Laptop",
            description="High-performance laptop created via gRPC",
            price_per_unit=149999,
            count_in_stock=10,
            state=1  # AVAILABLE
        )
        
        assert product.id
        assert product.name == "gRPC Test Gaming Laptop"
        assert product.description == "High-performance laptop created via gRPC"
        assert product.price_per_unit == 149999
        assert product.count_in_stock == 10
        assert product.state == 1

    def test_create_product_minimal_data(self, inventory_grpc_client: InventoryServiceClient):
        """Step 7: CreateProduct - with minimal required fields."""
        product = inventory_grpc_client.create_product(
            name="gRPC Minimal Product",
            price_per_unit=999,
            count_in_stock=5
        )
        
        assert product.id
        assert product.name == "gRPC Minimal Product"
        assert product.price_per_unit == 999
        assert product.count_in_stock == 5

    def test_create_product_invalid_price(self, inventory_grpc_client: InventoryServiceClient):
        """Step 8: CreateProduct - with invalid price (should fail)."""
        with pytest.raises(Exception) as exc_info:
            inventory_grpc_client.create_product(
                name="Invalid Price Product",
                price_per_unit=0,
                count_in_stock=1
            )
        
        assert "INVALID_ARGUMENT" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()

    def test_create_product_invalid_stock(self, inventory_grpc_client: InventoryServiceClient):
        """Step 9: CreateProduct - with negative stock (should fail)."""
        with pytest.raises(Exception) as exc_info:
            inventory_grpc_client.create_product(
                name="Negative Stock Product",
                price_per_unit=1000,
                count_in_stock=-5
            )
        
        assert "INVALID_ARGUMENT" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()

    def test_update_product_single_field(self, inventory_grpc_client: InventoryServiceClient):
        """Step 10: UpdateProduct - update single field."""
        # Create a product first
        product = inventory_grpc_client.create_product(
            name="Product to Update",
            price_per_unit=5000,
            count_in_stock=10
        )
        
        # Update just the name
        updated = inventory_grpc_client.update_product(
            product_id=product.id,
            name="Updated Product Name"
        )
        
        assert updated.name == "Updated Product Name"
        assert updated.price_per_unit == 5000  # Unchanged
        assert updated.count_in_stock == 10  # Unchanged

    def test_update_product_multiple_fields(self, inventory_grpc_client: InventoryServiceClient):
        """Step 11: UpdateProduct - update multiple fields."""
        # Create a product first
        product = inventory_grpc_client.create_product(
            name="Multi Update Product",
            price_per_unit=3000,
            count_in_stock=5
        )
        
        # Update multiple fields
        updated = inventory_grpc_client.update_product(
            product_id=product.id,
            name="New Name",
            price_per_unit=4000,
            count_in_stock=15
        )
        
        assert updated.name == "New Name"
        assert updated.price_per_unit == 4000
        assert updated.count_in_stock == 15

    def test_update_product_state(self, inventory_grpc_client: InventoryServiceClient):
        """Step 12: UpdateProduct - change product state."""
        # Create a product
        product = inventory_grpc_client.create_product(
            name="State Change Product",
            price_per_unit=2000,
            count_in_stock=8,
            state=1  # AVAILABLE
        )
        
        # Change to OFF_SHELF
        updated = inventory_grpc_client.update_product(
            product_id=product.id,
            state=2  # OFF_SHELF
        )
        
        assert updated.state == 2

    def test_update_product_not_found(self, inventory_grpc_client: InventoryServiceClient):
        """Step 13: UpdateProduct - non-existent product."""
        with pytest.raises(Exception) as exc_info:
            inventory_grpc_client.update_product(
                product_id="non-existent-id",
                name="Should Fail"
            )
        
        assert "NOT_FOUND" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_delete_product(self, inventory_grpc_client: InventoryServiceClient):
        """Step 14: DeleteProduct - soft delete."""
        # Create a product
        product = inventory_grpc_client.create_product(
            name="Product to Delete",
            price_per_unit=1500,
            count_in_stock=3
        )
        
        # Delete it
        inventory_grpc_client.delete_product(product.id)
        
        # Try to get it (may fail or return with deleted flag)
        with pytest.raises(Exception):
            inventory_grpc_client.get_product(product.id)

    def test_delete_product_not_found(self, inventory_grpc_client: InventoryServiceClient):
        """Step 15: DeleteProduct - non-existent product."""
        with pytest.raises(Exception) as exc_info:
            inventory_grpc_client.delete_product("non-existent-id")
        
        assert "NOT_FOUND" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_query_products_pagination(self, inventory_grpc_client: InventoryServiceClient):
        """Step 16: QueryProducts - pagination with cursor."""
        # First page
        first_response = inventory_grpc_client.query_products(first=10)
        
        if not first_response.page_info.has_next_page:
            pytest.skip("Not enough products for pagination test")
        
        # Second page
        end_cursor = first_response.page_info.end_cursor
        second_response = inventory_grpc_client.query_products(first=10, after=end_cursor)
        
        # No duplicate products
        first_ids = {p.id for p in first_response.products}
        second_ids = {p.id for p in second_response.products}
        assert len(first_ids & second_ids) == 0
        
        # Second page should have previous page
        assert second_response.page_info.has_previous_page

    def test_verify_timestamp_format(self, inventory_grpc_client: InventoryServiceClient, test_product_id: str):
        """Step 17: Verify timestamp format (google.protobuf.Timestamp)."""
        product = inventory_grpc_client.get_product(test_product_id)
        
        # Timestamps should be valid protobuf timestamps
        assert validate_grpc_timestamp(product.created_at)
        assert validate_grpc_timestamp(product.updated_at)

    def test_create_product_with_image_data(self, inventory_grpc_client: InventoryServiceClient):
        """Step 18: CreateProduct - with image data."""
        # Create base64 image data (not data URI, just raw bytes)
        import base64
        # Decode the base64 string to bytes
        image_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        product = inventory_grpc_client.create_product(
            name="Product with Image",
            description="Has image data",
            image_data=image_bytes,
            price_per_unit=2500,
            count_in_stock=7
        )
        
        assert product.id
        # The protobuf field is bytes, so compare bytes
        assert product.image_data == image_bytes
