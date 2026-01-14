# API-TC010: gRPC OrderService API

## Summary
Verify that the Transaction Service gRPC OrderService correctly handles all order operations including creating orders from carts, querying orders with pagination and filters, getting single orders, and updating order states.

## Description
This test case validates the backend gRPC OrderService which manages customer orders. It tests all RPC methods defined in the service: CreateOrder, QueryOrders, GetOrder, and UpdateOrder. It validates order creation from cart contents, state machine enforcement, pagination, filtering, and order data integrity.

## Prerequisites
- Transaction service (transd) is running and accessible on gRPC port (default: 9090)
- Database is accessible and writable
- Database contains products with state AVAILABLE and sufficient stock
- CartService is functional (for creating orders)
- gRPC client tool available (grpcurl, BloomRPC, or custom client)
- Service implements: demoshop.v1.OrderService

## Test Steps

### Step 1: CreateOrder - From Cart with Items
**Setup:** Create cart and add products:
```bash
# Add products to cart
grpcurl -plaintext -d '{
  "cart_id": "order-test-cart-001",
  "product_id": "product-001",
  "quantity": 2
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "order-test-cart-001",
  "product_id": "product-002",
  "quantity": 3
}' localhost:9090 demoshop.v1.CartService/AddProductToCart
```

**Action:** Call CreateOrder RPC:
```bash
grpcurl -plaintext -d '{
  "cart_id": "order-test-cart-001"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder
```

**Expected Result:**
- RPC succeeds with status OK
- Order created with unique ID
- Order contains cart items
- Initial state is PROCESSING

**Validation:**
- Response contains `order` object
- `order.id` is non-empty unique string
- `order.items` length = 2
- `order.items[0]` and `order.items[1]` match cart products
- Each `order.items[].product` is product snapshot
- Each `order.items[].quantity` matches cart quantities
- Each `order.items[].price_at_purchase` matches product price
- `order.total_amount` = sum of (quantity × price_at_purchase) for all items
- `order.state` = 1 (PROCESSING enum value)
- `order.created_at` is recent timestamp
- `order.updated_at` equals `order.created_at`

**Save order ID for subsequent tests.**

**Post-Validation:** Verify cart is cleared:
```bash
grpcurl -plaintext -d '{
  "cart_id": "order-test-cart-001"
}' localhost:9090 demoshop.v1.CartService/GetCart
```
- `cart.items` should be empty

### Step 2: CreateOrder - From Empty Cart
**Setup:** Create or clear cart to make it empty:
```bash
grpcurl -plaintext -d '{
  "cart_id": "empty-cart"
}' localhost:9090 demoshop.v1.CartService/ClearCart
```

**Action:** Try to create order from empty cart:
```bash
grpcurl -plaintext -d '{
  "cart_id": "empty-cart"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- Cannot create order from empty cart

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9) or INVALID_ARGUMENT (3)
- Error message indicates empty cart or no items
- No order created

### Step 3: CreateOrder - From Non-Existent Cart
**Action:** Try to create order with invalid cart ID:
```bash
grpcurl -plaintext -d '{
  "cart_id": "non-existent-cart-999"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder
```

**Expected Result:**
- RPC fails with NOT_FOUND status
- Cart not found

**Validation:**
- gRPC status code = NOT_FOUND (5)
- Error message indicates cart not found
- No order created

### Step 4: GetOrder - Valid Order ID
**Action:** Call GetOrder RPC with order from Step 1:
```bash
grpcurl -plaintext -d '{
  "id": "<order-id-from-step-1>"
}' localhost:9090 demoshop.v1.OrderService/GetOrder
```

**Expected Result:**
- RPC succeeds
- Returns complete order details

**Validation:**
- Response contains `order` object
- `order.id` matches requested ID
- `order.items` contains all order items
- Each item has product snapshot, quantity, price_at_purchase
- `order.total_amount` is accurate
- `order.state` = 1 (PROCESSING)
- `order.created_at` and `order.updated_at` are valid timestamps

### Step 5: GetOrder - Non-Existent Order
**Action:** Call GetOrder with invalid ID:
```bash
grpcurl -plaintext -d '{
  "id": "non-existent-order-999"
}' localhost:9090 demoshop.v1.OrderService/GetOrder
```

**Expected Result:**
- RPC fails with NOT_FOUND status

**Validation:**
- gRPC status code = NOT_FOUND (5)
- Error message indicates order not found

### Step 6: GetOrder - Empty Order ID
**Action:** Call GetOrder with empty ID:
```bash
grpcurl -plaintext -d '{
  "id": ""
}' localhost:9090 demoshop.v1.OrderService/GetOrder
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error indicates invalid or empty ID

### Step 7: QueryOrders - All Orders (No Filter)
**Action:** Call QueryOrders RPC:
```bash
grpcurl -plaintext -d '{
  "pagination": {
    "first": 20
  }
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC succeeds
- Returns list of orders with pagination
- Includes orders in all states

**Validation:**
- Response contains `orders` array
- Response contains `page_info` object
- Response contains `total_count` field
- `orders` length ≤ 20
- `page_info.has_next_page` reflects if more orders exist
- Each order has all required fields
- Orders include various states (PROCESSING, SHIPPED, COMPLETED, CANCELED)

### Step 8: QueryOrders - Filter by PROCESSING State
**Action:** Call QueryOrders with state filter:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 50},
  "state_filter": {
    "value": "PROCESSING"
  }
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC succeeds
- Returns only PROCESSING orders

**Validation:**
- All orders have `state` = 1 (PROCESSING)
- No orders with other states
- `total_count` reflects only PROCESSING orders

### Step 9: QueryOrders - Filter by SHIPPED State
**Action:** Call QueryOrders with SHIPPED filter:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 50},
  "state_filter": {
    "value": "SHIPPED"
  }
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC succeeds
- Returns only SHIPPED orders

**Validation:**
- All orders have `state` = 2 (SHIPPED)
- `total_count` = count of SHIPPED orders

### Step 10: QueryOrders - Filter by COMPLETED State
**Action:** Call QueryOrders with COMPLETED filter:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 50},
  "state_filter": {
    "value": "COMPLETED"
  }
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC succeeds
- Returns only COMPLETED orders

**Validation:**
- All orders have `state` = 3 (COMPLETED)
- `total_count` = count of COMPLETED orders

### Step 11: QueryOrders - Filter by CANCELED State
**Action:** Call QueryOrders with CANCELED filter:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 50},
  "state_filter": {
    "value": "CANCELED"
  }
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC succeeds
- Returns only CANCELED orders

**Validation:**
- All orders have `state` = 4 (CANCELED)
- `total_count` = count of CANCELED orders

### Step 12: QueryOrders - Pagination with Cursor
**Action:** Query first page and use cursor for second:
```bash
# First page
grpcurl -plaintext -d '{
  "pagination": {"first": 10}
}' localhost:9090 demoshop.v1.OrderService/QueryOrders

# Second page
grpcurl -plaintext -d '{
  "pagination": {
    "first": 10,
    "after": "<end_cursor_from_first_page>"
  }
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- Both RPCs succeed
- Second page returns next 10 orders
- No duplicates

**Validation:**
- First page returns 10 orders
- Second page returns next 10 orders
- No duplicate order IDs between pages
- `page_info.has_previous_page` = true on second page
- `total_count` consistent across both calls

### Step 13: UpdateOrder - PROCESSING to SHIPPED
**Setup:** Use order in PROCESSING state from Step 1

**Action:** Call UpdateOrder to change state to SHIPPED:
```bash
grpcurl -plaintext -d '{
  "id": "<order-id-from-step-1>",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC succeeds
- Order state changed to SHIPPED
- updated_at timestamp updated

**Validation:**
- `order.id` unchanged
- `order.state` = 2 (SHIPPED, was PROCESSING)
- `order.updated_at` > `order.created_at`
- `order.items` and `order.total_amount` unchanged
- Only state and updated_at changed

### Step 14: UpdateOrder - SHIPPED to COMPLETED
**Action:** Call UpdateOrder to complete the order:
```bash
grpcurl -plaintext -d '{
  "id": "<order-id-from-step-1>",
  "state": "COMPLETED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC succeeds
- Order state changed to COMPLETED

**Validation:**
- `order.state` = 3 (COMPLETED, was SHIPPED)
- `order.updated_at` updated
- Valid state transition

### Step 15: UpdateOrder - PROCESSING to CANCELED
**Setup:** Create new order in PROCESSING state:
```bash
# Create cart with items
grpcurl -plaintext -d '{
  "cart_id": "cancel-test-cart",
  "product_id": "product-003",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

# Create order
grpcurl -plaintext -d '{
  "cart_id": "cancel-test-cart"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder
```

**Action:** Cancel the order:
```bash
grpcurl -plaintext -d '{
  "id": "<new-order-id>",
  "state": "CANCELED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC succeeds
- Order canceled from PROCESSING state

**Validation:**
- `order.state` = 4 (CANCELED, was PROCESSING)
- `order.updated_at` updated
- Valid state transition

### Step 16: UpdateOrder - SHIPPED to CANCELED
**Setup:** Create order and ship it:
```bash
# Create cart and order
grpcurl -plaintext -d '{
  "cart_id": "shipped-cancel-cart",
  "product_id": "product-004",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "shipped-cancel-cart"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder

# Ship it
grpcurl -plaintext -d '{
  "id": "<new-order-id>",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Action:** Cancel the shipped order:
```bash
grpcurl -plaintext -d '{
  "id": "<new-order-id>",
  "state": "CANCELED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC succeeds
- Order canceled from SHIPPED state

**Validation:**
- `order.state` = 4 (CANCELED, was SHIPPED)
- Valid state transition

### Step 17: UpdateOrder - Invalid Transition (PROCESSING to COMPLETED)
**Setup:** Create order in PROCESSING state

**Action:** Try to complete without shipping:
```bash
grpcurl -plaintext -d '{
  "id": "<processing-order-id>",
  "state": "COMPLETED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- Invalid state transition

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9)
- Error message indicates invalid state transition
- Order state unchanged (remains PROCESSING)

### Step 18: UpdateOrder - Invalid Transition (COMPLETED to SHIPPED)
**Setup:** Use completed order from Step 14

**Action:** Try to ship completed order:
```bash
grpcurl -plaintext -d '{
  "id": "<completed-order-id>",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- Cannot change COMPLETED order

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9)
- Error indicates invalid transition
- Order state unchanged (remains COMPLETED)
- COMPLETED is terminal state

### Step 19: UpdateOrder - Invalid Transition (COMPLETED to CANCELED)
**Action:** Try to cancel completed order:
```bash
grpcurl -plaintext -d '{
  "id": "<completed-order-id>",
  "state": "CANCELED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- Cannot cancel completed order

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9)
- Order state unchanged (remains COMPLETED)

### Step 20: UpdateOrder - Invalid Transition (CANCELED to SHIPPED)
**Setup:** Use canceled order

**Action:** Try to ship canceled order:
```bash
grpcurl -plaintext -d '{
  "id": "<canceled-order-id>",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status
- CANCELED is terminal state

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9)
- Order state unchanged (remains CANCELED)

### Step 21: UpdateOrder - Invalid Transition (CANCELED to COMPLETED)
**Action:** Try to complete canceled order:
```bash
grpcurl -plaintext -d '{
  "id": "<canceled-order-id>",
  "state": "COMPLETED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC fails with FAILED_PRECONDITION status

**Validation:**
- gRPC status code = FAILED_PRECONDITION (9)
- Order state unchanged

### Step 22: UpdateOrder - Transition to Same State (Idempotent)
**Action:** Try to set order to its current state:
```bash
grpcurl -plaintext -d '{
  "id": "<shipped-order-id>",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC succeeds (no-op) or fails
- Idempotent operation

**Validation:**
- Either succeeds with no changes
- Or returns error indicating no change
- Order state remains SHIPPED
- Behavior is consistent

### Step 23: UpdateOrder - Non-Existent Order
**Action:** Try to update non-existent order:
```bash
grpcurl -plaintext -d '{
  "id": "non-existent-order-999",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- RPC fails with NOT_FOUND status

**Validation:**
- gRPC status code = NOT_FOUND (5)
- Error message indicates order not found

### Step 24: Verify Order Total Calculation
**Setup:** Create order with known items and prices

**Action:** 
1. Add products to cart with known prices
2. Create order
3. Verify total

```bash
# Add products (assume product-005: 1000, product-006: 2500)
grpcurl -plaintext -d '{
  "cart_id": "total-calc-cart",
  "product_id": "product-005",
  "quantity": 3
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "total-calc-cart",
  "product_id": "product-006",
  "quantity": 2
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

# Create order
grpcurl -plaintext -d '{
  "cart_id": "total-calc-cart"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder
```

**Expected Result:**
- Order total accurately calculated

**Validation:**
- Item 1: quantity=3, price_at_purchase=1000, subtotal=3000
- Item 2: quantity=2, price_at_purchase=2500, subtotal=5000
- `order.total_amount` = 8000
- Calculation accurate, no overflow

### Step 25: Verify Product Snapshot Immutability
**Action:**
1. Create order with product
2. Update product in inventory
3. Query order again

```bash
# Create order (done in previous steps)
# Update product price
grpcurl -plaintext -d '{
  "id": "product-001",
  "price_per_unit": {"value": 99999}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct

# Query order
grpcurl -plaintext -d '{
  "id": "<order-id-with-product-001>"
}' localhost:9090 demoshop.v1.OrderService/GetOrder
```

**Expected Result:**
- Order items contain immutable product snapshots
- Prices don't change with inventory updates

**Validation:**
- `order.items[].product.price_per_unit` = original price (not 99999)
- `order.items[].price_at_purchase` = original price
- `order.total_amount` unchanged
- Product snapshot is immutable

### Step 26: QueryOrders - Empty Pagination
**Action:** Call QueryOrders without pagination:
```bash
grpcurl -plaintext -d '{}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC succeeds with default pagination

**Validation:**
- Orders returned (default page size, likely 20 or 50)
- `page_info` included
- `total_count` included

### Step 27: QueryOrders - Large Page Size
**Action:** Call QueryOrders with large page size:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 500}
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC succeeds
- Returns up to 500 orders
- Performance acceptable

**Validation:**
- Orders length ≤ 500
- Response time < 5 seconds
- `total_count` reflects all orders

### Step 28: QueryOrders - Zero Page Size
**Action:** Call QueryOrders with zero page size:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 0}
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT or returns empty

**Validation:**
- Either status = INVALID_ARGUMENT (3)
- Or returns empty orders array
- Behavior is consistent

### Step 29: Verify Order State Enum Values
**Action:** Query orders and verify state enum:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 20}
}' localhost:9090 demoshop.v1.OrderService/QueryOrders
```

**Expected Result:**
- State values are valid enum integers
- 0 = UNSPECIFIED (should not appear)
- 1 = PROCESSING
- 2 = SHIPPED
- 3 = COMPLETED
- 4 = CANCELED

**Validation:**
- All `order.state` values are 1, 2, 3, or 4
- No state = 0 (UNSPECIFIED)
- State enum properly encoded

### Step 30: Verify Valid State Transition Sequence
**Action:** Create order and transition through full lifecycle:
```bash
# Create order
grpcurl -plaintext -d '{
  "cart_id": "lifecycle-cart",
  "product_id": "product-007",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "lifecycle-cart"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder

# Ship
grpcurl -plaintext -d '{
  "id": "<new-order-id>",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder

# Complete
grpcurl -plaintext -d '{
  "id": "<new-order-id>",
  "state": "COMPLETED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder
```

**Expected Result:**
- All transitions succeed
- Order moves through proper lifecycle

**Validation:**
- Initial: state = PROCESSING
- After ship: state = SHIPPED
- After complete: state = COMPLETED
- Valid lifecycle: PROCESSING → SHIPPED → COMPLETED

### Step 31: Verify Timestamp Updates on State Changes
**Action:** Update order state and check timestamps:
```bash
# Get order before update
grpcurl -plaintext -d '{
  "id": "<order-id>"
}' localhost:9090 demoshop.v1.OrderService/GetOrder

# Update state
grpcurl -plaintext -d '{
  "id": "<order-id>",
  "state": "SHIPPED"
}' localhost:9090 demoshop.v1.OrderService/UpdateOrder

# Get order after update
grpcurl -plaintext -d '{
  "id": "<order-id>"
}' localhost:9090 demoshop.v1.OrderService/GetOrder
```

**Expected Result:**
- updated_at changes on state update
- created_at never changes

**Validation:**
- `updated_at` after > `updated_at` before
- `created_at` unchanged
- Timestamps accurate

### Step 32: CreateOrder - Multiple Orders from Same Cart
**Action:**
1. Create cart with items
2. Create first order
3. Add items to cart again
4. Create second order

```bash
# First order
grpcurl -plaintext -d '{
  "cart_id": "multi-order-cart",
  "product_id": "product-008",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "multi-order-cart"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder

# Second order
grpcurl -plaintext -d '{
  "cart_id": "multi-order-cart",
  "product_id": "product-009",
  "quantity": 1
}' localhost:9090 demoshop.v1.CartService/AddProductToCart

grpcurl -plaintext -d '{
  "cart_id": "multi-order-cart"
}' localhost:9090 demoshop.v1.OrderService/CreateOrder
```

**Expected Result:**
- Both orders created successfully
- Each has unique ID
- Cart cleared after each order

**Validation:**
- First order ID ≠ second order ID
- Both orders exist independently
- Each order has correct items
- Cart empty after each CreateOrder

## Success Criteria
- ✅ CreateOrder successfully creates order from cart with items
- ✅ CreateOrder clears cart after successful order creation
- ✅ CreateOrder fails with empty or non-existent cart
- ✅ Orders have unique IDs and initialize to PROCESSING state
- ✅ Order items contain immutable product snapshots
- ✅ Order total accurately calculated from items
- ✅ GetOrder returns complete order details for valid IDs
- ✅ QueryOrders returns orders with proper pagination
- ✅ State filter correctly filters orders by state
- ✅ UpdateOrder enforces valid state transitions
- ✅ Valid transitions: PROCESSING→SHIPPED→COMPLETED, PROCESSING/SHIPPED→CANCELED
- ✅ Invalid transitions rejected with FAILED_PRECONDITION
- ✅ Terminal states (COMPLETED, CANCELED) cannot be changed
- ✅ Timestamps (created_at, updated_at) accurate and consistent
- ✅ Non-existent orders return NOT_FOUND
- ✅ Invalid IDs and parameters return INVALID_ARGUMENT
- ✅ Data integrity maintained across all operations

## Notes
- Valid state transitions:
  - PROCESSING (1) → SHIPPED (2)
  - SHIPPED (2) → COMPLETED (3)
  - PROCESSING (1) → CANCELED (4)
  - SHIPPED (2) → CANCELED (4)
- Invalid transitions: PROCESSING→COMPLETED, any from COMPLETED or CANCELED
- Order.State enum: 0=UNSPECIFIED, 1=PROCESSING, 2=SHIPPED, 3=COMPLETED, 4=CANCELED
- OrderItem contains product snapshot at time of order creation
- Product snapshots are immutable (prices don't change)
- price_at_purchase field preserves price at order time
- Timestamps use google.protobuf.Timestamp format
- total_amount is sum of (quantity × price_at_purchase) for all items
- CreateOrder clears the cart after successful order creation
- gRPC status codes: OK=0, INVALID_ARGUMENT=3, NOT_FOUND=5, FAILED_PRECONDITION=9
