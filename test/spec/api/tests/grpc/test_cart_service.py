"""
API-TC009: gRPC CartService API

Test gRPC CartService operations.
Tests GetCart, AddProductToCart, UpdateProductInCart, ClearCart.
"""
import pytest
import uuid
from utils.grpc_client import CartServiceClient, InventoryServiceClient


@pytest.mark.grpc
@pytest.mark.integration
class TestGRPCCartService:
    """Test gRPC CartService (API-TC009)."""

    def test_get_cart_auto_creation(self, cart_grpc_client: CartServiceClient):
        """Step 1: GetCart - non-existent cart (auto-creation)."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        cart = cart_grpc_client.get_cart(cart_id)
        
        assert cart.id == cart_id
        assert len(cart.items) == 0
        assert hasattr(cart, 'created_at')
        assert hasattr(cart, 'updated_at')

    def test_add_product_to_cart_first_item(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 2: AddProductToCart - first product."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        cart = cart_grpc_client.add_product_to_cart(
            cart_id=cart_id,
            product_id=test_product_id,
            quantity=1
        )
        
        assert cart.id == cart_id
        assert len(cart.items) == 1
        assert cart.items[0].product.id == test_product_id
        assert cart.items[0].quantity == 1

    def test_add_same_product_increments(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 3: AddProductToCart - same product again (increments quantity)."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add product first time
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 2)
        
        # Add same product again
        cart = cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 3)
        
        # Should still have one item with incremented quantity
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5  # 2 + 3

    def test_add_different_products(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_ids: list
    ):
        """Step 4: AddProductToCart - different products."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add first product
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[0], 2)
        
        # Add second product
        cart = cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[1], 3)
        
        # Should have two items
        assert len(cart.items) == 2
        
        product_ids = {item.product.id for item in cart.items}
        assert test_product_ids[0] in product_ids
        assert test_product_ids[1] in product_ids

    def test_add_product_invalid_quantity(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 5: AddProductToCart - invalid quantity."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Try to add with zero or negative quantity
        with pytest.raises(Exception) as exc_info:
            cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 0)
        
        assert "INVALID_ARGUMENT" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()

    def test_add_non_existent_product(self, cart_grpc_client: CartServiceClient):
        """Step 6: AddProductToCart - non-existent product."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        with pytest.raises(Exception) as exc_info:
            cart_grpc_client.add_product_to_cart(cart_id, "non-existent-product", 1)
        
        assert "NOT_FOUND" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_update_product_increase_quantity(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 7: UpdateProductInCart - increase quantity."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add product first
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 3)
        
        # Update to higher quantity
        cart = cart_grpc_client.update_product_in_cart(cart_id, test_product_id, 10)
        
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 10  # Set to exact value, not incremented

    def test_update_product_decrease_quantity(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_id: str
    ):
        """Step 8: UpdateProductInCart - decrease quantity."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add product with high quantity
        cart_grpc_client.add_product_to_cart(cart_id, test_product_id, 10)
        
        # Decrease quantity
        cart = cart_grpc_client.update_product_in_cart(cart_id, test_product_id, 2)
        
        assert cart.items[0].quantity == 2

    def test_update_product_zero_removes(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_ids: list
    ):
        """Step 9: UpdateProductInCart - set to zero removes item."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add two products
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[0], 5)
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[1], 3)
        
        # Set first product to zero
        cart = cart_grpc_client.update_product_in_cart(cart_id, test_product_ids[0], 0)
        
        # Should only have one item now
        assert len(cart.items) == 1
        assert cart.items[0].product.id == test_product_ids[1]

    def test_update_product_not_in_cart(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_ids: list
    ):
        """Step 10: UpdateProductInCart - product not in cart."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add one product
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[0], 2)
        
        # Try to update different product not in cart
        with pytest.raises(Exception) as exc_info:
            cart_grpc_client.update_product_in_cart(cart_id, test_product_ids[1], 5)
        
        assert "NOT_FOUND" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_clear_cart(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_ids: list
    ):
        """Step 11: ClearCart - remove all items."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add multiple products
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[0], 1)
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[1], 2)
        cart_grpc_client.add_product_to_cart(cart_id, test_product_ids[2], 3)
        
        # Clear cart
        cart = cart_grpc_client.clear_cart(cart_id)
        
        assert len(cart.items) == 0

    def test_clear_empty_cart(self, cart_grpc_client: CartServiceClient):
        """Step 12: ClearCart - already empty cart."""
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Get cart (auto-creates empty cart)
        cart_grpc_client.get_cart(cart_id)
        
        # Clear already empty cart
        cart = cart_grpc_client.clear_cart(cart_id)
        
        assert len(cart.items) == 0

    def test_add_product_insufficient_stock(
        self, 
        cart_grpc_client: CartServiceClient,
        inventory_grpc_client: InventoryServiceClient
    ):
        """Step 13: AddProductToCart - insufficient stock."""
        # Create a product with limited stock
        product = inventory_grpc_client.create_product(
            name="Limited Stock Product",
            price_per_unit=1000,
            count_in_stock=2
        )
        
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Try to add more than available
        with pytest.raises(Exception) as exc_info:
            cart_grpc_client.add_product_to_cart(cart_id, product.id, 10)
        
        assert "FAILED_PRECONDITION" in str(exc_info.value) or "insufficient" in str(exc_info.value).lower()

    def test_add_off_shelf_product(
        self, 
        cart_grpc_client: CartServiceClient,
        inventory_grpc_client: InventoryServiceClient
    ):
        """Step 14: AddProductToCart - OFF_SHELF product."""
        # Create an OFF_SHELF product
        product = inventory_grpc_client.create_product(
            name="Off Shelf Product",
            price_per_unit=1500,
            count_in_stock=5,
            state=2  # OFF_SHELF
        )
        
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Try to add OFF_SHELF product
        with pytest.raises(Exception) as exc_info:
            cart_grpc_client.add_product_to_cart(cart_id, product.id, 1)
        
        assert "FAILED_PRECONDITION" in str(exc_info.value) or "not available" in str(exc_info.value).lower()

    def test_verify_product_snapshot(
        self, 
        cart_grpc_client: CartServiceClient,
        inventory_grpc_client: InventoryServiceClient
    ):
        """Step 15: Verify product snapshot in cart."""
        # Create a product
        product = inventory_grpc_client.create_product(
            name="Snapshot Test Product",
            price_per_unit=3000,
            count_in_stock=10
        )
        
        cart_id = f"test-cart-{uuid.uuid4()}"
        
        # Add to cart
        cart = cart_grpc_client.add_product_to_cart(cart_id, product.id, 2)
        
        # Product details should be in cart item
        cart_item = cart.items[0]
        assert cart_item.product.id == product.id
        assert cart_item.product.name == product.name
        assert cart_item.product.price_per_unit == product.price_per_unit

    def test_multiple_carts_isolation(
        self, 
        cart_grpc_client: CartServiceClient,
        test_product_ids: list
    ):
        """Step 16: Verify multiple carts are isolated."""
        cart_id1 = f"test-cart-{uuid.uuid4()}"
        cart_id2 = f"test-cart-{uuid.uuid4()}"
        
        # Add products to first cart
        cart_grpc_client.add_product_to_cart(cart_id1, test_product_ids[0], 3)
        
        # Add different products to second cart
        cart_grpc_client.add_product_to_cart(cart_id2, test_product_ids[1], 5)
        
        # Get both carts
        cart1 = cart_grpc_client.get_cart(cart_id1)
        cart2 = cart_grpc_client.get_cart(cart_id2)
        
        # Verify isolation
        assert len(cart1.items) == 1
        assert cart1.items[0].product.id == test_product_ids[0]
        
        assert len(cart2.items) == 1
        assert cart2.items[0].product.id == test_product_ids[1]
