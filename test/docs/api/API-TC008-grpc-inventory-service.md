# API-TC008: gRPC InventoryService API

## Summary
Verify that the Transaction Service gRPC InventoryService correctly handles all inventory operations including querying products with pagination and filters, getting single products, creating products, updating products, and deleting products.

## Description
This test case validates the backend gRPC InventoryService which manages the product inventory. It tests all RPC methods defined in the service: QueryProducts, GetProduct, CreateProduct, UpdateProduct, and DeleteProduct. It validates request/response message structures, data types, field updates, pagination, filtering, and error handling.

## Prerequisites
- Transaction service (transd) is running and accessible on gRPC port (default: 9090)
- Database is accessible and writable
- gRPC client tool available (grpcurl, BloomRPC, or custom client)
- Service implements: demoshop.v1.InventoryService

## Test Steps

### Step 1: QueryProducts - All Products (No Filter)
**Action:** Call QueryProducts RPC with basic pagination:
```bash
grpcurl -plaintext -d '{
  "pagination": {
    "first": 20
  }
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- RPC succeeds with status OK
- Returns list of products with pagination info
- Products include all states

**Validation:**
- Response contains `products` array
- Response contains `page_info` object
- Response contains `total_count` field
- `products` length ≤ 20
- `page_info.has_next_page` reflects if more products exist
- `page_info.has_previous_page` = false
- Each product has all required fields: id, name, price_per_unit, count_in_stock, state, created_at, updated_at

### Step 2: QueryProducts - Filter by AVAILABLE State
**Action:** Call QueryProducts with state filter:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 50},
  "state_filter": "AVAILABLE"
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- RPC succeeds
- Returns only AVAILABLE products
- Total count reflects filtered results

**Validation:**
- All products have `state` = 1 (AVAILABLE enum value)
- No products with state 2 (OFF_SHELF)
- `total_count` = number of AVAILABLE products

### Step 3: QueryProducts - Filter by OFF_SHELF State
**Action:** Call QueryProducts with OFF_SHELF filter:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 50},
  "state_filter": "OFF_SHELF"
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- RPC succeeds
- Returns only OFF_SHELF products

**Validation:**
- All products have `state` = 2 (OFF_SHELF enum value)
- No products with state 1 (AVAILABLE)
- `total_count` = number of OFF_SHELF products

### Step 4: QueryProducts - Pagination with Cursor
**Action:** Query first page and use cursor for second page:
```bash
# First page
grpcurl -plaintext -d '{
  "pagination": {"first": 10}
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts

# Second page using end_cursor from first response
grpcurl -plaintext -d '{
  "pagination": {
    "first": 10,
    "after": "<end_cursor_from_first_page>"
  }
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- Both RPCs succeed
- Second page returns next 10 products
- No duplicates between pages

**Validation:**
- First page returns 10 products
- Second page returns next 10 products
- Product IDs are different between pages
- No duplicate products
- `page_info.has_previous_page` = true on second page
- `total_count` consistent across both calls

### Step 5: GetProduct - Valid Product ID
**Action:** Call GetProduct RPC:
```bash
grpcurl -plaintext -d '{
  "id": "product-001"
}' localhost:9090 demoshop.v1.InventoryService/GetProduct
```

**Expected Result:**
- RPC succeeds with status OK
- Returns product details

**Validation:**
- Response contains `product` object
- `product.id` = "product-001"
- `product.name` is non-empty
- `product.price_per_unit` > 0
- `product.count_in_stock` ≥ 0
- `product.state` is 1 or 2 (AVAILABLE or OFF_SHELF)
- `product.created_at` is valid timestamp
- `product.updated_at` is valid timestamp
- `product.updated_at` >= `product.created_at`

### Step 6: GetProduct - Non-Existent Product
**Action:** Call GetProduct with invalid ID:
```bash
grpcurl -plaintext -d '{
  "id": "non-existent-product-999"
}' localhost:9090 demoshop.v1.InventoryService/GetProduct
```

**Expected Result:**
- RPC fails with NOT_FOUND status
- Error message indicates product not found

**Validation:**
- gRPC status code = NOT_FOUND (5)
- Error message contains "not found" or similar
- No product returned

### Step 7: GetProduct - Empty Product ID
**Action:** Call GetProduct with empty ID:
```bash
grpcurl -plaintext -d '{
  "id": ""
}' localhost:9090 demoshop.v1.InventoryService/GetProduct
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Error indicates invalid ID

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates invalid or empty ID

### Step 8: CreateProduct - Complete Product Data
**Action:** Call CreateProduct RPC with all fields:
```bash
grpcurl -plaintext -d '{
  "name": "Test Wireless Mouse",
  "description": "Ergonomic wireless mouse with 6 buttons",
  "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "price_per_unit": 2999,
  "count_in_stock": 50,
  "state": "AVAILABLE"
}' localhost:9090 demoshop.v1.InventoryService/CreateProduct
```

**Expected Result:**
- RPC succeeds with status OK
- Product created with unique ID
- All fields saved correctly

**Validation:**
- Response contains `product` object
- `product.id` is non-empty unique string
- `product.name` = "Test Wireless Mouse"
- `product.description` = "Ergonomic wireless mouse with 6 buttons"
- `product.image_data` is base64 encoded bytes
- `product.price_per_unit` = 2999
- `product.count_in_stock` = 50
- `product.state` = 1 (AVAILABLE)
- `product.created_at` is recent timestamp
- `product.updated_at` equals `product.created_at`

**Save product ID for subsequent tests.**

### Step 9: CreateProduct - Minimal Required Fields
**Action:** Call CreateProduct with only required fields:
```bash
grpcurl -plaintext -d '{
  "name": "Minimal Product",
  "price_per_unit": 999,
  "count_in_stock": 10
}' localhost:9090 demoshop.v1.InventoryService/CreateProduct
```

**Expected Result:**
- RPC succeeds
- Product created with default values for optional fields
- Default state is AVAILABLE

**Validation:**
- `product.id` is non-empty
- `product.name` = "Minimal Product"
- `product.description` is empty
- `product.image_data` is empty
- `product.price_per_unit` = 999
- `product.count_in_stock` = 10
- `product.state` = 1 (AVAILABLE default)

### Step 10: CreateProduct - Missing Required Field (Name)
**Action:** Call CreateProduct without name:
```bash
grpcurl -plaintext -d '{
  "price_per_unit": 1000,
  "count_in_stock": 5
}' localhost:9090 demoshop.v1.InventoryService/CreateProduct
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Error indicates missing name

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates missing or invalid name field

### Step 11: CreateProduct - Invalid Price (Zero)
**Action:** Call CreateProduct with zero price:
```bash
grpcurl -plaintext -d '{
  "name": "Zero Price Product",
  "price_per_unit": 0,
  "count_in_stock": 5
}' localhost:9090 demoshop.v1.InventoryService/CreateProduct
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Price must be positive

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates invalid price

### Step 12: CreateProduct - Negative Stock Count
**Action:** Call CreateProduct with negative stock:
```bash
grpcurl -plaintext -d '{
  "name": "Negative Stock Product",
  "price_per_unit": 1000,
  "count_in_stock": -5
}' localhost:9090 demoshop.v1.InventoryService/CreateProduct
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Stock cannot be negative

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates invalid stock count

### Step 13: UpdateProduct - Update Name
**Action:** Call UpdateProduct to change name:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "name": {
    "value": "Updated Wireless Mouse Pro"
  }
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- Product name updated
- Other fields unchanged
- updated_at timestamp updated

**Validation:**
- `product.id` unchanged
- `product.name` = "Updated Wireless Mouse Pro"
- `product.description` unchanged from Step 8
- `product.price_per_unit` unchanged
- `product.count_in_stock` unchanged
- `product.state` unchanged
- `product.created_at` unchanged
- `product.updated_at` > `product.created_at`

### Step 14: UpdateProduct - Update Price
**Action:** Call UpdateProduct to change price:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "price_per_unit": {
    "value": 3499
  }
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- Product price updated
- Name remains as updated in Step 13

**Validation:**
- `product.price_per_unit` = 3499
- `product.name` = "Updated Wireless Mouse Pro" (from Step 13)
- `product.updated_at` reflects latest update

### Step 15: UpdateProduct - Update Stock Count
**Action:** Call UpdateProduct to change stock:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "count_in_stock": {
    "value": 100
  }
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- Stock count updated

**Validation:**
- `product.count_in_stock` = 100
- Previous updates preserved
- `product.updated_at` updated

### Step 16: UpdateProduct - Update State to OFF_SHELF
**Action:** Call UpdateProduct to change state:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "state": {
    "value": "OFF_SHELF"
  }
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- Product state changed to OFF_SHELF

**Validation:**
- `product.state` = 2 (OFF_SHELF)
- All other fields unchanged
- `product.updated_at` updated

### Step 17: UpdateProduct - Update Multiple Fields
**Action:** Call UpdateProduct with multiple fields:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-9>",
  "name": {"value": "Updated Minimal Product"},
  "description": {"value": "Now has a description"},
  "price_per_unit": {"value": 1499},
  "count_in_stock": {"value": 25},
  "state": {"value": "OFF_SHELF"}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- All specified fields updated in single operation

**Validation:**
- `product.name` = "Updated Minimal Product"
- `product.description` = "Now has a description"
- `product.price_per_unit` = 1499
- `product.count_in_stock` = 25
- `product.state` = 2 (OFF_SHELF)
- `product.updated_at` reflects single update time

### Step 18: UpdateProduct - Update Description and Image
**Action:** Call UpdateProduct to set description and image:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "description": {"value": "Premium wireless mouse with RGB lighting"},
  "image_data": {"value": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- Description and image updated

**Validation:**
- `product.description` = "Premium wireless mouse with RGB lighting"
- `product.image_data` is updated base64 bytes
- Previous updates preserved
- `product.updated_at` updated

### Step 19: UpdateProduct - Non-Existent Product
**Action:** Call UpdateProduct with invalid ID:
```bash
grpcurl -plaintext -d '{
  "id": "non-existent-product-999",
  "name": {"value": "Should Fail"}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC fails with NOT_FOUND status

**Validation:**
- gRPC status code = NOT_FOUND (5)
- Error message indicates product not found

### Step 20: UpdateProduct - Invalid Price Update
**Action:** Call UpdateProduct with zero/negative price:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "price_per_unit": {"value": 0}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Price must remain positive

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error message indicates invalid price
- Product price unchanged

### Step 21: UpdateProduct - Update State Back to AVAILABLE
**Action:** Call UpdateProduct to toggle state:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "state": {"value": "AVAILABLE"}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- State changed back to AVAILABLE

**Validation:**
- `product.state` = 1 (AVAILABLE)
- `product.updated_at` updated

### Step 22: UpdateProduct - Set Stock to Zero
**Action:** Call UpdateProduct to set stock to 0:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>",
  "count_in_stock": {"value": 0}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct
```

**Expected Result:**
- RPC succeeds
- Zero stock is valid

**Validation:**
- `product.count_in_stock` = 0
- Update successful
- Out of stock but product still exists

### Step 23: DeleteProduct - Valid Product
**Action:** Call DeleteProduct RPC:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-9>"
}' localhost:9090 demoshop.v1.InventoryService/DeleteProduct
```

**Expected Result:**
- RPC succeeds with status OK
- Product deleted (soft or hard delete)

**Validation:**
- RPC returns empty response (DeleteProductResponse)
- No error returned

**Post-Validation:** Try to get the deleted product:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-9>"
}' localhost:9090 demoshop.v1.InventoryService/GetProduct
```
- Should return NOT_FOUND or product with deleted flag

### Step 24: DeleteProduct - Non-Existent Product
**Action:** Call DeleteProduct with invalid ID:
```bash
grpcurl -plaintext -d '{
  "id": "non-existent-product-999"
}' localhost:9090 demoshop.v1.InventoryService/DeleteProduct
```

**Expected Result:**
- RPC fails with NOT_FOUND status or succeeds (idempotent)

**Validation:**
- Either gRPC status = NOT_FOUND (5)
- Or succeeds with empty response (idempotent delete)
- Behavior is consistent

### Step 25: DeleteProduct - Empty Product ID
**Action:** Call DeleteProduct with empty ID:
```bash
grpcurl -plaintext -d '{
  "id": ""
}' localhost:9090 demoshop.v1.InventoryService/DeleteProduct
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error indicates invalid ID

### Step 26: QueryProducts - Empty Pagination
**Action:** Call QueryProducts without pagination:
```bash
grpcurl -plaintext -d '{}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- RPC succeeds with default pagination
- Default page size applied

**Validation:**
- Products returned (likely default of 20 or 50)
- `page_info` included
- `total_count` included

### Step 27: QueryProducts - Large Page Size
**Action:** Call QueryProducts with large page size:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 500}
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- RPC succeeds
- Returns up to 500 products
- Performance acceptable

**Validation:**
- Products length ≤ 500
- Response time < 5 seconds
- `total_count` reflects all products

### Step 28: QueryProducts - Zero Page Size
**Action:** Call QueryProducts with zero page size:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 0}
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT or returns empty
- Zero is invalid page size

**Validation:**
- Either status = INVALID_ARGUMENT (3)
- Or returns empty products array
- Behavior is consistent

### Step 29: QueryProducts - Invalid Cursor
**Action:** Call QueryProducts with invalid cursor:
```bash
grpcurl -plaintext -d '{
  "pagination": {
    "first": 10,
    "after": "invalid-cursor-value"
  }
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- RPC fails with INVALID_ARGUMENT status
- Invalid cursor rejected

**Validation:**
- gRPC status code = INVALID_ARGUMENT (3)
- Error indicates invalid cursor

### Step 30: Verify Timestamp Format
**Action:** Call GetProduct and verify timestamp fields:
```bash
grpcurl -plaintext -d '{
  "id": "<product-id-from-step-8>"
}' localhost:9090 demoshop.v1.InventoryService/GetProduct
```

**Expected Result:**
- Timestamps are google.protobuf.Timestamp format
- Timestamps are logically consistent

**Validation:**
- `created_at` has `seconds` and `nanos` fields
- `updated_at` has `seconds` and `nanos` fields
- `updated_at` >= `created_at`
- Timestamps are valid Unix timestamps

### Step 31: Verify Product State Enum Values
**Action:** Query products and verify state enum:
```bash
grpcurl -plaintext -d '{
  "pagination": {"first": 10}
}' localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

**Expected Result:**
- State values are valid enum integers
- 0 = UNSPECIFIED (should not appear)
- 1 = AVAILABLE
- 2 = OFF_SHELF

**Validation:**
- All `product.state` values are 1 or 2
- No state = 0 (UNSPECIFIED)
- State enum properly encoded

### Step 32: Create and Immediately Query Product
**Action:**
1. Create product
2. Immediately query it by ID

```bash
# Create
grpcurl -plaintext -d '{
  "name": "Immediate Query Test",
  "price_per_unit": 1234,
  "count_in_stock": 5
}' localhost:9090 demoshop.v1.InventoryService/CreateProduct

# Query (use ID from create response)
grpcurl -plaintext -d '{
  "id": "<new-product-id>"
}' localhost:9090 demoshop.v1.InventoryService/GetProduct
```

**Expected Result:**
- Product immediately available after creation
- No delay or eventual consistency issues

**Validation:**
- GetProduct succeeds
- Product data matches creation input
- No caching or consistency issues

### Step 33: Concurrent Updates
**Action:** Execute multiple updates to same product concurrently (if possible):
```bash
# Update 1: Change name
grpcurl -plaintext -d '{
  "id": "<product-id>",
  "name": {"value": "Concurrent Update 1"}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct &

# Update 2: Change price
grpcurl -plaintext -d '{
  "id": "<product-id>",
  "price_per_unit": {"value": 9999}
}' localhost:9090 demoshop.v1.InventoryService/UpdateProduct &
```

**Expected Result:**
- Both updates succeed
- No data corruption
- Final state reflects both updates

**Validation:**
- Both RPCs return success
- Product has both name and price updates
- No lost updates
- Data integrity maintained

## Success Criteria
- ✅ QueryProducts returns products with correct pagination
- ✅ State filter works correctly (AVAILABLE, OFF_SHELF)
- ✅ Cursor-based pagination traverses all products without duplicates
- ✅ GetProduct returns complete product details for valid IDs
- ✅ GetProduct returns NOT_FOUND for invalid IDs
- ✅ CreateProduct succeeds with complete or minimal data
- ✅ CreateProduct validates required fields and value ranges
- ✅ UpdateProduct modifies only specified fields
- ✅ UpdateProduct preserves unmodified fields
- ✅ UpdateProduct updates updated_at timestamp
- ✅ UpdateProduct validates field values (price > 0, etc.)
- ✅ DeleteProduct removes products from queries
- ✅ All operations handle invalid IDs with appropriate errors
- ✅ Timestamps use google.protobuf.Timestamp format
- ✅ State enum values are correct (1=AVAILABLE, 2=OFF_SHELF)
- ✅ Products immediately queryable after creation
- ✅ Concurrent updates handled correctly

## Notes
- This is the backend gRPC API, not the GraphQL frontend API
- Product.State enum: 0=UNSPECIFIED, 1=AVAILABLE, 2=OFF_SHELF
- Timestamps use google.protobuf.Timestamp (seconds + nanos)
- UpdateProduct uses wrapped types (NameUpdate, PricePerUnitUpdate, etc.) for partial updates
- Only fields present in update request are modified
- image_data is bytes type (base64 decoded in protobuf)
- Default gRPC port is usually 9090
- Use `grpcurl -plaintext localhost:9090 list` to verify service availability
