# API-TC006: Admin Product CRUD Operations

## Summary
Verify that administrators can create, update, and delete products through GraphQL API mutations.

## Description
This test case validates admin product management operations including creating new products with various field combinations, updating single or multiple fields, toggling product state on/off shelf, and soft-deleting products. It tests field validation, data integrity, and proper error handling.

## Prerequisites
- Frontend service is running and admin GraphQL endpoint is accessible
- Admin authentication/authorization in place (if implemented)
- Transaction service is running with Inventory service
- Database is writable
- Test image data in base64 format available

## Test Steps

### Step 1: Create Product with Complete Data
**Action:** Execute createProduct mutation with all fields:
```graphql
mutation {
  createProduct(input: {
    name: "Test Gaming Laptop"
    description: "High-performance gaming laptop with RGB keyboard"
    imageData: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    pricePerUnit: 129999
    countInStock: 15
    state: AVAILABLE
  }) {
    id
    name
    description
    imageData
    pricePerUnit
    countInStock
    state
    createdAt
    updatedAt
  }
}
```

**Expected Result:**
- Product created successfully
- All fields saved correctly
- Unique ID assigned
- Timestamps generated

**Validation:**
- `id` is non-empty unique string
- `name` = "Test Gaming Laptop"
- `description` = "High-performance gaming laptop with RGB keyboard"
- `imageData` starts with "data:image/png;base64,"
- `pricePerUnit` = 129999
- `countInStock` = 15
- `state` = "AVAILABLE"
- `createdAt` is valid recent timestamp
- `updatedAt` equals `createdAt`

**Save product ID for subsequent tests.**

### Step 2: Create Product with Minimal Data
**Action:** Execute createProduct with only required fields:
```graphql
mutation {
  createProduct(input: {
    name: "Simple Product"
    pricePerUnit: 999
    countInStock: 10
  }) {
    id
    name
    description
    imageData
    pricePerUnit
    countInStock
    state
    createdAt
  }
}
```

**Expected Result:**
- Product created successfully
- Optional fields null or default values
- Default state is AVAILABLE

**Validation:**
- `id` is non-empty
- `name` = "Simple Product"
- `description` is null or empty
- `imageData` is null or empty
- `pricePerUnit` = 999
- `countInStock` = 10
- `state` = "AVAILABLE" (default)
- `createdAt` is valid

### Step 3: Create Product with State OFF_SHELF
**Action:** Execute createProduct with initial state OFF_SHELF:
```graphql
mutation {
  createProduct(input: {
    name: "Coming Soon Product"
    description: "Product launching next month"
    pricePerUnit: 4999
    countInStock: 0
    state: OFF_SHELF
  }) {
    id
    name
    state
    countInStock
  }
}
```

**Expected Result:**
- Product created with OFF_SHELF state
- Zero stock is allowed

**Validation:**
- `id` is non-empty
- `name` = "Coming Soon Product"
- `state` = "OFF_SHELF"
- `countInStock` = 0
- Product created successfully

### Step 4: Create Product with Missing Required Field (Name)
**Action:** Execute createProduct without name:
```graphql
mutation {
  createProduct(input: {
    pricePerUnit: 1000
    countInStock: 5
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns GraphQL validation error
- Required field validation

**Validation:**
- Response contains GraphQL error
- Error message indicates missing required field `name`
- No product created

### Step 5: Create Product with Empty Name
**Action:** Execute createProduct with empty string name:
```graphql
mutation {
  createProduct(input: {
    name: ""
    pricePerUnit: 1000
    countInStock: 5
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Empty name not allowed

**Validation:**
- Response contains error
- Error message indicates invalid name
- No product created

### Step 6: Create Product with Invalid Price
**Action:** Execute createProduct with zero or negative price:
```graphql
mutation {
  createProduct(input: {
    name: "Invalid Price Product"
    pricePerUnit: 0
    countInStock: 5
  }) {
    id
  }
}

mutation {
  createProduct(input: {
    name: "Negative Price Product"
    pricePerUnit: -100
    countInStock: 5
  }) {
    id
  }
}
```

**Expected Result:**
- Both mutations return errors
- Price must be positive

**Validation:**
- Both responses contain errors
- Error messages indicate invalid price
- No products created

### Step 7: Create Product with Negative Stock
**Action:** Execute createProduct with negative countInStock:
```graphql
mutation {
  createProduct(input: {
    name: "Negative Stock Product"
    pricePerUnit: 1000
    countInStock: -5
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Stock cannot be negative

**Validation:**
- Response contains error
- Error message indicates invalid stock count
- No product created

### Step 8: Update Product Name
**Action:** Execute updateProduct to change name:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    name: "Updated Gaming Laptop Pro"
  }) {
    id
    name
    description
    pricePerUnit
    updatedAt
  }
}
```

**Expected Result:**
- Product name updated
- Other fields unchanged
- updatedAt timestamp updated

**Validation:**
- `name` = "Updated Gaming Laptop Pro"
- `description` unchanged from Step 1
- `pricePerUnit` unchanged from Step 1
- `updatedAt` > `createdAt` (from Step 1)
- Other fields remain as originally set

### Step 9: Update Product Price
**Action:** Execute updateProduct to change price:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    pricePerUnit: 139999
  }) {
    id
    name
    pricePerUnit
    updatedAt
  }
}
```

**Expected Result:**
- Product price updated
- Name remains as updated in Step 8

**Validation:**
- `pricePerUnit` = 139999
- `name` = "Updated Gaming Laptop Pro" (from Step 8)
- `updatedAt` > previous updatedAt

### Step 10: Update Product Stock Count
**Action:** Execute updateProduct to change stock:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    countInStock: 25
  }) {
    id
    countInStock
    updatedAt
  }
}
```

**Expected Result:**
- Product stock updated
- Other fields unchanged

**Validation:**
- `countInStock` = 25
- Previous updates (name, price) preserved
- `updatedAt` reflects latest update

### Step 11: Update Product Description and Image
**Action:** Execute updateProduct to change description and image:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    description: "Premium gaming laptop with latest GPU and 32GB RAM"
    imageData: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD/2wBD..."
  }) {
    id
    description
    imageData
    updatedAt
  }
}
```

**Expected Result:**
- Description and image updated
- Other fields unchanged

**Validation:**
- `description` = "Premium gaming laptop with latest GPU and 32GB RAM"
- `imageData` starts with "data:image/jpeg;base64,"
- Previous updates preserved
- `updatedAt` updated

### Step 12: Update Multiple Fields Simultaneously
**Action:** Execute updateProduct with multiple fields:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-2>"
    name: "Updated Simple Product"
    description: "Now with description"
    pricePerUnit: 1299
    countInStock: 20
  }) {
    id
    name
    description
    pricePerUnit
    countInStock
    updatedAt
  }
}
```

**Expected Result:**
- All specified fields updated
- Single update operation

**Validation:**
- `name` = "Updated Simple Product"
- `description` = "Now with description"
- `pricePerUnit` = 1299
- `countInStock` = 20
- `updatedAt` reflects single update time

### Step 13: Update Non-Existent Product
**Action:** Execute updateProduct with invalid ID:
```graphql
mutation {
  updateProduct(input: {
    id: "non-existent-product-id-999"
    name: "Should Fail"
  }) {
    id
    name
  }
}
```

**Expected Result:**
- Mutation returns error
- Product not found

**Validation:**
- Response contains error
- Error message indicates product not found
- No product created or modified

### Step 14: Update Product with Empty Name
**Action:** Execute updateProduct with empty string name:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    name: ""
  }) {
    id
    name
  }
}
```

**Expected Result:**
- Mutation returns error
- Empty name not allowed

**Validation:**
- Response contains error
- Error message indicates invalid name
- Product name unchanged

### Step 15: Update Product with Invalid Price
**Action:** Execute updateProduct with zero/negative price:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    pricePerUnit: 0
  }) {
    id
  }
}

mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    pricePerUnit: -1000
  }) {
    id
  }
}
```

**Expected Result:**
- Both mutations return errors
- Price must remain positive

**Validation:**
- Both responses contain errors
- Product price unchanged
- Previous valid price preserved

### Step 16: Update Product State via putProductOnShelf
**Action:** Take OFF_SHELF product and put on shelf:
```graphql
mutation {
  putProductOnShelf(id: "<product-id-from-step-3>") {
    id
    state
    updatedAt
  }
}
```

**Expected Result:**
- Product state changed to AVAILABLE
- updatedAt timestamp updated

**Validation:**
- `state` = "AVAILABLE" (was OFF_SHELF)
- `updatedAt` > previous value
- Product ID unchanged

### Step 17: Update Product State via takeProductOffShelf
**Action:** Take AVAILABLE product off shelf:
```graphql
mutation {
  takeProductOffShelf(id: "<product-id-from-step-1>") {
    id
    state
    updatedAt
  }
}
```

**Expected Result:**
- Product state changed to OFF_SHELF
- updatedAt timestamp updated

**Validation:**
- `state` = "OFF_SHELF" (was AVAILABLE)
- `updatedAt` > previous value
- Other fields unchanged

### Step 18: Toggle Product State Multiple Times
**Action:** Toggle state on → off → on:
```graphql
mutation {
  putProductOnShelf(id: "<product-id-from-step-2>") {
    id
    state
  }
}

mutation {
  takeProductOffShelf(id: "<product-id-from-step-2>") {
    id
    state
  }
}

mutation {
  putProductOnShelf(id: "<product-id-from-step-2>") {
    id
    state
  }
}
```

**Expected Result:**
- Each toggle works correctly
- State changes each time

**Validation:**
- After first mutation: `state` = "AVAILABLE"
- After second mutation: `state` = "OFF_SHELF"
- After third mutation: `state` = "AVAILABLE"
- All operations successful

### Step 19: Update State via updateProduct Mutation
**Action:** Execute updateProduct with state field:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    state: AVAILABLE
  }) {
    id
    state
    updatedAt
  }
}
```

**Expected Result:**
- Product state updated
- Alternative method to state toggle mutations

**Validation:**
- `state` = "AVAILABLE"
- `updatedAt` updated
- Works as alternative to putProductOnShelf/takeProductOffShelf

### Step 20: Remove Product (Soft Delete)
**Action:** Execute removeProduct mutation:
```graphql
mutation {
  removeProduct(id: "<product-id-from-step-2>")
}
```

**Expected Result:**
- Mutation returns true
- Product soft-deleted (not physically removed)

**Validation:**
- Mutation returns `true`
- Query to verify product still exists but marked deleted (if applicable)
- Or product no longer appears in standard product queries

**Post-Validation:** Try to query the product:
```graphql
query {
  product(id: "<product-id-from-step-2>") {
    id
    name
  }
}
```
- Product may return null or with deleted flag depending on implementation

### Step 21: Remove Non-Existent Product
**Action:** Execute removeProduct with invalid ID:
```graphql
mutation {
  removeProduct(id: "non-existent-product-999")
}
```

**Expected Result:**
- Mutation returns error or false
- No errors thrown

**Validation:**
- Returns `false` or error message
- Error indicates product not found
- No system errors

### Step 22: Try to Update Deleted Product
**Action:** Execute updateProduct on deleted product:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-2>"
    name: "Should Not Work"
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Deleted products cannot be updated

**Validation:**
- Response contains error
- Error indicates product not found or deleted
- Update rejected

### Step 23: Create Product with Special Characters
**Action:** Execute createProduct with special characters:
```graphql
mutation {
  createProduct(input: {
    name: "Product with Special Chars: @#$%^&*()"
    description: "Description with <script>alert('xss')</script> and quotes \"test\""
    pricePerUnit: 5000
    countInStock: 10
  }) {
    id
    name
    description
  }
}
```

**Expected Result:**
- Product created successfully
- Special characters sanitized or escaped
- No XSS vulnerability

**Validation:**
- Product created
- `name` preserves safe special characters
- `description` has HTML/script tags sanitized
- No script execution
- Data stored safely

### Step 24: Create Product with Unicode Characters
**Action:** Execute createProduct with Unicode:
```graphql
mutation {
  createProduct(input: {
    name: "Gaming Laptop ゲーミングノートPC 游戏笔记本"
    description: "Международный продукт"
    pricePerUnit: 99999
    countInStock: 5
  }) {
    id
    name
    description
  }
}
```

**Expected Result:**
- Product created successfully
- Unicode characters preserved

**Validation:**
- `name` = "Gaming Laptop ゲーミングノートPC 游戏笔记本"
- `description` = "Международный продукт"
- Unicode stored and retrieved correctly

### Step 25: Create Product with Very Long Name
**Action:** Execute createProduct with long name:
```graphql
mutation {
  createProduct(input: {
    name: "A Very Long Product Name That Goes On And On And Contains Many Words To Test The Maximum Length Allowed For Product Names In The System Which Should Have Some Reasonable Limit To Prevent Database Issues And Display Problems In The User Interface"
    pricePerUnit: 1000
    countInStock: 5
  }) {
    id
    name
  }
}
```

**Expected Result:**
- Product created successfully
- Or error if exceeds max length

**Validation:**
- If max length limit exists: error returned with limit info
- If no limit: full name stored
- Behavior is consistent and documented

### Step 26: Update Product to Set Stock to Zero
**Action:** Execute updateProduct to set stock to 0:
```graphql
mutation {
  updateProduct(input: {
    id: "<product-id-from-step-1>"
    countInStock: 0
  }) {
    id
    countInStock
    state
  }
}
```

**Expected Result:**
- Stock updated to zero
- Product remains in current state
- Zero stock is valid

**Validation:**
- `countInStock` = 0
- `state` unchanged (OFF_SHELF from Step 17)
- Update successful

### Step 27: Verify Updated Product via Query
**Action:** Query product updated in previous steps:
```graphql
query {
  product(id: "<product-id-from-step-1>") {
    id
    name
    description
    pricePerUnit
    countInStock
    state
    createdAt
    updatedAt
  }
}
```

**Expected Result:**
- Product reflects all updates
- CreatedAt unchanged, updatedAt shows latest update

**Validation:**
- All fields match latest updates from Steps 8-11, 17, 26
- `createdAt` equals original timestamp from Step 1
- `updatedAt` > `createdAt`
- Data integrity maintained

### Step 28: Create Large Batch of Products
**Action:** Execute multiple createProduct mutations:
```graphql
mutation { createProduct(input: {name: "Batch Product 1", pricePerUnit: 1000, countInStock: 10}) { id } }
mutation { createProduct(input: {name: "Batch Product 2", pricePerUnit: 2000, countInStock: 20}) { id } }
mutation { createProduct(input: {name: "Batch Product 3", pricePerUnit: 3000, countInStock: 30}) { id } }
# ... repeat for 10 products
```

**Expected Result:**
- All products created successfully
- Each with unique ID
- No conflicts or errors

**Validation:**
- All mutations successful
- All product IDs unique
- Can query all created products
- No data corruption

## Success Criteria
- ✅ Products created successfully with complete or minimal data
- ✅ Required fields (name, pricePerUnit, countInStock) validated
- ✅ Optional fields (description, imageData) handle null values
- ✅ Default state is AVAILABLE if not specified
- ✅ Product updates modify only specified fields
- ✅ Multiple fields can be updated simultaneously
- ✅ State can be toggled via dedicated mutations or updateProduct
- ✅ Invalid data (empty name, negative price/stock) rejected
- ✅ Non-existent products return appropriate errors
- ✅ Soft delete removes products from standard queries
- ✅ Timestamps (createdAt, updatedAt) accurate and consistent
- ✅ Special characters and Unicode handled correctly
- ✅ No XSS vulnerabilities
- ✅ Each product has unique ID
- ✅ Updates preserve unchanged fields
- ✅ Zero stock is valid value

## Notes
- Product ID is assigned by system and immutable
- CreatedAt timestamp never changes after creation
- UpdatedAt timestamp reflects latest modification
- Soft delete may keep product in database with deleted flag
- Price in cents (integer) avoids floating-point errors
- Image data should follow data URI scheme: "data:image/{type};base64,{data}"
- State AVAILABLE means product visible to customers
- State OFF_SHELF means product hidden from customers
- Stock count of zero is valid (out of stock but product exists)
