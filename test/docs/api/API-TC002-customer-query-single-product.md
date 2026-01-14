# API-TC002: Customer Query Single Product

## Summary
Verify that customers can query detailed information for a specific product by ID through the GraphQL `product` query.

## Description
This test case validates the customer-facing `product` query which returns detailed information about a single product. The query should return products regardless of their state (unlike the products list), allowing customers to view product pages they may have bookmarked or linked from elsewhere. It validates product data completeness, handles non-existent products, and ensures proper error responses.

## Prerequisites
- Frontend service is running and GraphQL endpoint is accessible
- Database contains products in various states (AVAILABLE, OFF_SHELF)
- At least one product with complete data (name, description, image, price, stock)
- At least one product with minimal data (no description or image)
- Known product IDs for testing

## Test Steps

### Step 1: Query Product with Complete Data
**Action:** Execute GraphQL query for a product with all fields populated:
```graphql
query {
  product(id: "product-001") {
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
- Query returns successfully with HTTP 200
- Product data is complete and accurate
- All fields are populated correctly

**Validation:**
- Response contains `product` object (not null)
- `id` = "product-001"
- `name` is non-empty string
- `description` is non-empty string
- `imageData` is non-empty string starting with "data:image/"
- `pricePerUnit` is positive integer
- `countInStock` is non-negative integer
- `state` is either "AVAILABLE" or "OFF_SHELF"
- `createdAt` is valid ISO 8601 timestamp
- `updatedAt` is valid ISO 8601 timestamp
- `updatedAt` ≥ `createdAt`

### Step 2: Query AVAILABLE Product
**Action:** Execute query for a product with state AVAILABLE:
```graphql
query {
  product(id: "available-product-id") {
    id
    name
    state
    countInStock
    pricePerUnit
  }
}
```

**Expected Result:**
- Query returns successfully
- Product state is AVAILABLE
- Product has stock available

**Validation:**
- `state` = "AVAILABLE"
- `countInStock` > 0
- `pricePerUnit` > 0
- Product data is accurate

### Step 3: Query OFF_SHELF Product
**Action:** Execute query for a product with state OFF_SHELF:
```graphql
query {
  product(id: "off-shelf-product-id") {
    id
    name
    state
    countInStock
    pricePerUnit
  }
}
```

**Expected Result:**
- Query returns successfully
- Product state is OFF_SHELF
- Product data is returned (unlike list query which excludes OFF_SHELF)

**Validation:**
- `state` = "OFF_SHELF"
- Product data is complete
- Query succeeds even though product is off shelf

### Step 4: Query Product with No Description
**Action:** Execute query for product missing optional fields:
```graphql
query {
  product(id: "minimal-product-id") {
    id
    name
    description
    imageData
    pricePerUnit
    countInStock
    state
  }
}
```

**Expected Result:**
- Query returns successfully
- Optional fields are null
- Required fields are populated

**Validation:**
- `id` is non-empty
- `name` is non-empty
- `description` is null or empty
- `imageData` is null or empty
- `pricePerUnit` > 0
- `countInStock` ≥ 0
- `state` is valid enum value

### Step 5: Query Out-of-Stock Product
**Action:** Execute query for product with countInStock = 0:
```graphql
query {
  product(id: "out-of-stock-product-id") {
    id
    name
    countInStock
    state
    pricePerUnit
  }
}
```

**Expected Result:**
- Query returns successfully
- Product shows zero stock
- Customer can still view product details

**Validation:**
- `countInStock` = 0
- All other fields populated correctly
- Query succeeds (product page accessible even when out of stock)

### Step 6: Query Non-Existent Product
**Action:** Execute query with invalid/non-existent product ID:
```graphql
query {
  product(id: "non-existent-product-id-99999") {
    id
    name
    pricePerUnit
  }
}
```

**Expected Result:**
- Query returns successfully with HTTP 200
- Product is null
- No error thrown (null is valid response)

**Validation:**
- `product` is null
- No error in response
- Or returns error with appropriate message like "Product not found"

### Step 7: Query with Empty Product ID
**Action:** Execute query with empty string as product ID:
```graphql
query {
  product(id: "") {
    id
    name
  }
}
```

**Expected Result:**
- Query returns error or null product
- Error message indicates invalid ID

**Validation:**
- HTTP status 200 or 400
- Error response indicates invalid input
- Or `product` is null

### Step 8: Query with Null Product ID
**Action:** Execute query without providing product ID:
```graphql
query {
  product {
    id
    name
  }
}
```

**Expected Result:**
- Query returns GraphQL validation error
- Error indicates required argument missing

**Validation:**
- Response contains GraphQL error
- Error message mentions missing required argument `id`
- HTTP status may be 400

### Step 9: Query Product with Special Characters in ID
**Action:** Execute query with product ID containing special characters:
```graphql
query {
  product(id: "product-with-special-chars-@#$%") {
    id
    name
  }
}
```

**Expected Result:**
- Query handles special characters safely
- Returns null if product doesn't exist
- No SQL injection or system errors

**Validation:**
- Query executes safely
- No system errors or crashes
- Returns null or appropriate error
- No indication of backend vulnerabilities

### Step 10: Query Subset of Fields
**Action:** Execute query requesting only specific fields:
```graphql
query {
  product(id: "product-001") {
    id
    name
    pricePerUnit
  }
}
```

**Expected Result:**
- Query returns only requested fields
- GraphQL field selection works correctly

**Validation:**
- Response contains only `id`, `name`, `pricePerUnit`
- Values are accurate
- Other fields not included in response

### Step 11: Verify Price Data Type and Format
**Action:** Query product and verify price is in correct format:
```graphql
query {
  product(id: "product-001") {
    id
    pricePerUnit
    name
  }
}
```

**Expected Result:**
- Price is returned as integer (in cents)
- No decimal places in price field

**Validation:**
- `pricePerUnit` is integer type
- Value is in smallest currency unit (cents)
- Value is positive
- Example: $19.99 should be 1999

### Step 12: Verify Image Data Format
**Action:** Query product with image and verify format:
```graphql
query {
  product(id: "product-with-image") {
    id
    imageData
  }
}
```

**Expected Result:**
- Image data follows data URI scheme
- Format is "data:image/{type};base64,{data}"

**Validation:**
- `imageData` starts with "data:image/"
- Contains ";base64," substring
- Base64 data follows the format
- Example: "data:image/png;base64,iVBORw0KG..."

### Step 13: Verify Timestamp Format
**Action:** Query product and verify timestamp formats:
```graphql
query {
  product(id: "product-001") {
    id
    createdAt
    updatedAt
  }
}
```

**Expected Result:**
- Timestamps are in ISO 8601 format
- Timestamps are logically consistent

**Validation:**
- `createdAt` matches pattern: YYYY-MM-DDTHH:MM:SS.sssZ or with timezone
- `updatedAt` matches same pattern
- `updatedAt` ≥ `createdAt`
- Timestamps are valid dates

### Step 14: Query Same Product Multiple Times
**Action:** Execute the same product query multiple times in succession:
```graphql
query {
  product(id: "product-001") {
    id
    name
    pricePerUnit
    countInStock
    updatedAt
  }
}
```

**Expected Result:**
- Queries return consistent results
- Data doesn't change between queries (assuming no updates)

**Validation:**
- All fields match across multiple queries
- Data is consistent and stable
- No random variations in response

### Step 15: Query Product After Adding to Cart
**Action:** 
1. Add product to cart via `addToCart` mutation
2. Query the same product via `product` query

```graphql
query {
  product(id: "product-001") {
    id
    countInStock
  }
}
```

**Expected Result:**
- Product query returns current state
- Stock count reflects system state (may or may not be decremented depending on business logic)

**Validation:**
- Product data is current
- Query succeeds independently of cart operations
- No errors from concurrent operations

## Success Criteria
- ✅ Product query returns accurate data for valid product IDs
- ✅ Query handles AVAILABLE and OFF_SHELF products correctly
- ✅ Optional fields (description, imageData) handle null values
- ✅ Query returns null for non-existent products without errors
- ✅ Invalid or malicious IDs handled safely
- ✅ Price is in correct format (integer cents)
- ✅ Image data follows data URI scheme format
- ✅ Timestamps are in ISO 8601 format
- ✅ Field selection works correctly (only requested fields returned)
- ✅ Queries are consistent and repeatable
- ✅ Out-of-stock products are accessible (unlike list query)
- ✅ No security vulnerabilities (SQL injection, XSS)

## Notes
- Unlike the `products` query, single `product` query returns products in any state
- This allows customers to view product pages even if product is temporarily off shelf
- Customers may have bookmarks or direct links to product pages
- Price is stored and returned in smallest currency unit (cents) to avoid decimal precision issues
- Image data uses data URI scheme for self-contained image representation
