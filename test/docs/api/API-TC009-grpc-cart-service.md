# API-TC009: gRPC CartService API

## Summary
Verify that the Transaction Service gRPC CartService correctly handles all cart operations including getting cart, adding products, updating quantities, and clearing cart.

## Description
This test case validates the backend gRPC CartService which manages shopping carts. It tests all RPC methods defined in the service: GetCart, AddProductToCart, UpdateProductInCart, and ClearCart. It validates cart auto-creation, product addition and removal, quantity management, and price calculations at the gRPC level.

## Prerequisites
- Transaction service (transd) is running and accessible on gRPC port (default: 9090)
- Database is accessible and writable
- Database contains at least 10 products with state AVAILABLE and count_in_stock > 5
- gRPC client tool available (grpcurl, BloomRPC, or custom client)
- Service implements: demoshop.v1.CartService

## Test Steps

### Step 1: GetCart - Non-Existent Cart (Auto-Creation)
**Action:** Call GetCart RPC with a new cart ID:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001"
}' localhost:9090 demoshop.v1.CartService/GetCart
```

**Expected Result:**
- RPC succeeds with status OK
- Cart is auto-created with the specified ID
- Cart is empty

**Validation:**
- Response contains `cart` object
- `cart.id` = "test-cart-001"
- `cart.items` is empty array
- `cart.created_at` is recent timestamp
- `cart.updated_at` equals `cart.created_at`

**Save cart ID for subsequent tests.**

### Step 2: AddProductToCart - First Product
**Action:** Call AddProductToCart with quantity 1:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-001",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC succeeds
- Product added to cart
- Cart contains one item

**Validation:**
- Response contains `cart` object
- `cart.id` = "test-cart-001"
- `cart.items` length = 1
- `cart.items[0].product.id` = "product-001"
- `cart.items[0].quantity` = 1
- `cart.items[0].product` contains full product snapshot (name, price_per_unit, etc.)
- `cart.updated_at` > `cart.created_at`

### Step 3: AddProductToCart - Same Product Again
**Action:** Add same product with quantity 2:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-001",
  "quantity": 2
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC succeeds
- Quantity increments for existing item
- No duplicate item created

**Validation:**
- `cart.items` length = 1 (still one item)
- `cart.items[0].product.id` = "product-001"
- `cart.items[0].quantity` = 3 (1 + 2)
- `cart.updated_at` updated

### Step 4: AddProductToCart - Different Product
**Action:** Add different product to cart:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-002",
  "quantity": 5
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC succeeds
- Second product added as new item
- Cart has two items

**Validation:**
- `cart.items` length = 2
- First item: `product.id` = "product-001", `quantity` = 3
- Second item: `product.id` = "product-002", `quantity` = 5
- Both items have complete product snapshots
- `cart.updated_at` updated

### Step 5: AddProductToCart - Large Quantity
**Action:** Add product with large quantity:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-003",
  "quantity": 100
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC succeeds
- Large quantity accepted (if within stock limits)

**Validation:**
- Cart contains item with `product.id` = "product-003"
- `quantity` = 100
- `cart.items` length = 3

### Step 6: AddProductToCart - Non-Existent Product
**Action:** Try to add non-existent product:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "non-existent-product-999",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with NOT_FOUND status
- Product not found

**Validation:**
- gRPC status code = NOT_FOUND (5)
- Error message indicates product not found
- Cart unchanged

### Step 7: AddProductToCart - Zero Quantity
**Action:** Try to add product with zero quantity:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-004",
  "quantity": 0
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Zero quantity not allowed for adding

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates invalid quantity
- Cart unchanged

### Step 8: AddProductToCart - Negative Quantity
**Action:** Try to add product with negative quantity:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-004",
  "quantity": -5
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Negative quantity not allowed

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates invalid quantity
- Cart unchanged

### Step 9: UpdateProductInCart - Increase Quantity
**Action:** Update product quantity to higher value:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-001",
  "quantity": 10
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart
```

**Expected Result:**
- RPC succeeds
- Quantity set to new value (not incremented)

**Validation:**
- Item with `product.id` = "product-001" has `quantity` = 10 (not 13)
- Other items unchanged
- `cart.updated_at` updated

### Step 10: UpdateProductInCart - Decrease Quantity
**Action:** Update product quantity to lower value:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-002",
  "quantity": 2
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart
```

**Expected Result:**
- RPC succeeds
- Quantity decreased
- Item remains in cart

**Validation:**
- Item with `product.id` = "product-002" has `quantity` = 2 (was 5)
- Item still exists in cart
- `cart.updated_at` updated

### Step 11: UpdateProductInCart - Set Quantity to Zero (Remove)
**Action:** Update product quantity to zero:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-003",
  "quantity": 0
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart
```

**Expected Result:**
- RPC succeeds
- Item removed from cart

**Validation:**
- Cart no longer contains item with `product.id` = "product-003"
- `cart.items` length = 2 (was 3)
- Other items unchanged
- `cart.updated_at` updated

### Step 12: UpdateProductInCart - Non-Existent Product
**Action:** Try to update product not in cart:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-not-in-cart",
  "quantity": 5
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart
```

**Expected Result:**
- RPC fails with NOT_FOUND status
- Product not in cart

**Validation:**
- gRPC status code = NOT_FOUND (5)
- Error indicates item not in cart
- Cart unchanged

### Step 13: UpdateProductInCart - Negative Quantity
**Action:** Try to set negative quantity:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-001",
  "quantity": -3
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Negative quantity not allowed

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates invalid quantity
- Cart unchanged

### Step 14: ClearCart - Remove All Items
**Action:** Call ClearCart RPC:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001"
}' localhost:9090 demoshop.v1.CartService/ClearCart
```

**Expected Result:**
- RPC succeeds
- Cart emptied

**Validation:**
- RPC returns empty response (ClearCartResponse)
- No error returned

**Post-Validation:** Query the cart:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001"
}' localhost:9090 demoshop.v1.CartService/GetCart
```
- `cart.items` is empty array
- `cart.id` still "test-cart-001" (cart exists but empty)
- `cart.updated_at` updated

### Step 15: AddProductToCart - After Clear
**Action:** Add product to previously cleared cart:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "product-005",
  "quantity": 3
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC succeeds
- Product added to empty cart

**Validation:**
- `cart.items` length = 1
- `cart.items[0].product.id` = "product-005"
- `cart.items[0].quantity` = 3

### Step 16: GetCart - After Modifications
**Action:** Query cart to verify current state:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001"
}' localhost:9090 demoshop.v1.CartService/GetCart
```

**Expected Result:**
- RPC succeeds
- Cart reflects all modifications

**Validation:**
- `cart.id` = "test-cart-001"
- `cart.items` reflects current state
- `cart.updated_at` > `cart.created_at`

### Step 17: ClearCart - Non-Existent Cart
**Action:** Try to clear non-existent cart:
```bash
grpcurl -plaintext -d '{
  "cart_id": "non-existent-cart-999"
}' localhost:9090 demoshop.v1.CartService/ClearCart
```

**Expected Result:**
- RPC succeeds (no-op) or fails with NOT_FOUND
- Idempotent operation

**Validation:**
- Either succeeds with empty response
- Or status = NOT_FOUND (5)
- Behavior is consistent

### Step 18: AddProductToCart - Empty Cart ID
**Action:** Try to add product with empty cart ID:
```bash
grpcurl -plaintext -d '{
  "cart_id": "",
  "product_id": "product-001",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Empty cart ID not allowed

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error indicates invalid cart ID

### Step 19: AddProductToCart - Empty Product ID
**Action:** Try to add product with empty product ID:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Empty product ID not allowed

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error indicates invalid product ID
- Cart unchanged

### Step 20: AddProductToCart - OFF_SHELF Product
**Setup:** Identify or create product with state OFF_SHELF

**Action:** Try to add OFF_SHELF product:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "<off-shelf-product-id>",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- OFF_SHELF products cannot be added

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9) or INVALID_ARGUMENT (3)
- Error message indicates product not available
- Cart unchanged

### Step 21: AddProductToCart - Out of Stock Product
**Setup:** Identify product with count_in_stock = 0

**Action:** Try to add out-of-stock product:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "<out-of-stock-product-id>",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- Out-of-stock products cannot be added

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9)
- Error message indicates insufficient stock
- Cart unchanged

### Step 22: AddProductToCart - Quantity Exceeds Stock
**Setup:** Identify product with limited stock (e.g., count_in_stock = 5)

**Action:** Try to add more than available:
```bash
grpcurl -plaintext -d '{
  "cart_id": "test-cart-001",
  "product_id": "<limited-stock-product-id>",
  "quantity": 100
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- Quantity exceeds available stock

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9)
- Error message indicates insufficient stock
- May include available stock count
- Cart unchanged

### Step 23: Verify Product Snapshot in Cart
**Setup:** Add product to cart, note its price

**Action:**
1. Add product to cart
2. Update product price in inventory
3. Query cart

```bash
# Add to cart
grpcurl -plaintext -d '{
  "cart_id": "test-cart-002",
  "product_id": "product-006",
  "quantity": 2
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

# Update product price (via InventoryService)
grpcurl -plaintext -d '{
  "id": "product-006",
  "price_per_unit": {"value": 99999}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct

# Query cart
grpcurl -plaintext -d '{
  "cart_id": "test-cart-002"
}' localhost:9090 demoshop.v1.CartService/GetCart
```

**Expected Result:**
- Cart contains product snapshot at time of addition
- Price in cart doesn't change with inventory update

**Validation:**
- `cart.items[0].product.price_per_unit` = original price (not 99999)
- Product snapshot is immutable in cart
- Or cart dynamically updates (depends on business logic)

### Step 24: Multiple Carts Isolation
**Action:** Create and manipulate multiple carts:
```bash
# Cart A
grpcurl -plaintext -d '{
  "cart_id": "cart-a",
  "product_id": "product-007",
  "quantity": 3
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

# Cart B
grpcurl -plaintext -d '{
  "cart_id": "cart-b",
  "product_id": "product-008",
  "quantity": 5
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

# Query both
grpcurl -plaintext -d '{"cart_id": "cart-a"}' localhost:9090 demoshop.v1.CartService/GetCart
grpcurl -plaintext -d '{"cart_id": "cart-b"}' localhost:9090 demoshop.v1.CartService/GetCart
```

**Expected Result:**
- Each cart maintains separate state
- Operations on one cart don't affect another

**Validation:**
- Cart A contains only product-007 with quantity 3
- Cart B contains only product-008 with quantity 5
- Carts are isolated

### Step 25: Verify Timestamp Updates
**Action:**
1. Create cart
2. Wait 1 second
3. Add product
4. Check timestamps

```bash
# Create/Get cart
grpcurl -plaintext -d '{
  "cart_id": "timestamp-test-cart"
}' localhost:9090 demoshop.v1.CartService/GetCart

# Wait and add product
sleep 1
grpcurl -plaintext -d '{
  "cart_id": "timestamp-test-cart",
  "product_id": "product-009",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- created_at remains unchanged
- updated_at reflects latest modification

**Validation:**
- `cart.created_at` unchanged from initial creation
- `cart.updated_at` > `cart.created_at` + 1 second
- Timestamps accurate

### Step 26: AddProductToCart - Multiple Products in Sequence
**Action:** Add multiple products one by one:
```bash
grpcurl -plaintext -d '{
  "cart_id": "multi-product-cart",
  "product_id": "product-010",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "multi-product-cart",
  "product_id": "product-011",
  "quantity": 2
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "multi-product-cart",
  "product_id": "product-012",
  "quantity": 3
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Expected Result:**
- All products added successfully
- Cart contains all three items

**Validation:**
- `cart.items` length = 3
- Each item has correct product and quantity
- Products added in order

### Step 27: UpdateProductInCart - Update All Items
**Action:** Update quantities for multiple items:
```bash
grpcurl -plaintext -d '{
  "cart_id": "multi-product-cart",
  "product_id": "product-010",
  "quantity": 5
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart

grpcurl -plaintext -d '{
  "cart_id": "multi-product-cart",
  "product_id": "product-011",
  "quantity": 10
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart

grpcurl -plaintext -d '{
  "cart_id": "multi-product-cart",
  "product_id": "product-012",
  "quantity": 15
}' localhost:9090 demoshop.v1.CartService/UpdateProductInCart
```

**Expected Result:**
- All updates succeed
- Quantities reflect new values

**Validation:**
- Item product-010: `quantity` = 5
- Item product-011: `quantity` = 10
- Item product-012: `quantity` = 15
- All updates applied correctly

### Step 28: Verify Cart Item Order
**Action:** Query cart and check item order:
```bash
grpcurl -plaintext -d '{
  "cart_id": "multi-product-cart"
}' localhost:9090 demoshop.v1.CartService/GetCart
```

**Expected Result:**
- Items returned in consistent order
- Order is deterministic

**Validation:**
- Items returned in same order on repeated queries
- Order may be by addition time or product ID
- Behavior is consistent

### Step 29: Concurrent Cart Operations
**Action:** Execute concurrent operations (if possible):
```bash
# Add product A
grpcurl -plaintext -d '{
  "cart_id": "concurrent-cart",
  "product_id": "product-013",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart &

# Add product B
grpcurl -plaintext -d '{
  "cart_id": "concurrent-cart",
  "product_id": "product-014",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart &
```

**Expected Result:**
- Both operations succeed
- No data corruption

**Validation:**
- Cart contains both products
- No lost updates
- Data integrity maintained

### Step 30: Verify Cart After Clear and Repopulate
**Action:**
1. Create cart with items
2. Clear cart
3. Add new items
4. Verify state

```bash
# Add items
grpcurl -plaintext -d '{
  "cart_id": "clear-test-cart",
  "product_id": "product-015",
  "quantity": 2
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

# Clear
grpcurl -plaintext -d '{
  "cart_id": "clear-test-cart"
}' localhost:9090 demoshop.v1.CartService/ClearCart

# Add new items
grpcurl -plaintext -d '{
  "cart_id": "clear-test-cart",
  "product_id": "product-016",
  "quantity": 5
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

# Verify
grpcurl -plaintext -d '{
  "cart_id": "clear-test-cart"
}' localhost:9090 demoshop.v1.CartService/GetCart
```

**Expected Result:**
- Cart completely reset after clear
- Only new items present

**Validation:**
- Cart contains only product-016
- No trace of product-015
- `cart.items` length = 1
- Cart ID unchanged

## Success Criteria
- ✅ GetCart auto-creates cart with specified ID if doesn't exist
- ✅ AddProductToCart adds products with correct quantities
- ✅ Adding same product increments quantity (no duplicates)
- ✅ AddProductToCart validates product existence and availability
- ✅ UpdateProductInCart sets quantity to exact value
- ✅ Setting quantity to zero removes item from cart
- ✅ ClearCart removes all items from cart
- ✅ Invalid operations return appropriate gRPC status codes
- ✅ Empty/invalid IDs return INVALID_ARGUMENT
- ✅ Non-existent products return NOT_FOUND
- ✅ OFF_SHELF and out-of-stock products return FAILED_PRECONDITION
- ✅ Negative and zero quantities rejected for AddProductToCart
- ✅ Product snapshots in cart (immutable or dynamic based on business logic)
- ✅ Multiple carts are isolated from each other
- ✅ Timestamps (created_at, updated_at) accurate and consistent
- ✅ Concurrent operations handled correctly

## Notes
- Cart IDs are provided by client (session-based)
- Cart auto-creates on first GetCart call
- Product snapshots may be immutable or update dynamically depending on business logic
- CartItem contains full product snapshot at time of addition
- Timestamps use google.protobuf.Timestamp format
- AddProductToCart increments quantity if product already in cart
- UpdateProductInCart sets absolute quantity value
- Setting quantity to 0 in UpdateProductInCart removes the item
- gRPC status codes: OK=0, INVALID_ARGUMENT=3, NOT_FOUND=5, FAILED_PRECONDITION=9
