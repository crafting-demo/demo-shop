# API-TC001: Customer Query Products

## Summary
Verify that customers can query available products with pagination through the GraphQL `products` query.

## Description
This test case validates the customer-facing `products` query which returns a paginated list of available products. The query should only return products with state `AVAILABLE` and exclude off-shelf or deleted products. It tests pagination parameters (`first`, `after`), validates the product data structure, and ensures proper cursor-based pagination.

## Prerequisites
- Frontend service is running and GraphQL endpoint is accessible
- Database contains at least 50 products with state `AVAILABLE`
- Database contains some products with state `OFF_SHELF` (should be excluded)
- Test products have varied data: names, descriptions, prices, stock counts, images

## Test Steps

### Step 1: Query First Page of Products (Default)
**Action:** Execute GraphQL query:
```graphql
query {
  products {
    edges {
      node {
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
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns successfully with HTTP 200
- Returns 20 products (default `first` value)
- All products have state `AVAILABLE`
- Products have `countInStock > 0`

**Validation:**
- `edges` array length = 20
- Each `node` has all required fields populated
- Each `node.state` = `AVAILABLE`
- Each `node.countInStock` > 0
- Each `node.pricePerUnit` is a positive integer
- `pageInfo.hasNextPage` is true (if more than 20 products exist)
- `pageInfo.hasPreviousPage` is false
- `pageInfo.totalCount` matches total available products
- `pageInfo.startCursor` and `pageInfo.endCursor` are non-empty strings
- All `cursor` values are unique and non-empty

### Step 2: Query Custom Page Size
**Action:** Execute GraphQL query with custom page size:
```graphql
query {
  products(first: 10) {
    edges {
      node {
        id
        name
        pricePerUnit
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns successfully
- Returns exactly 10 products
- Pagination info reflects the smaller page size

**Validation:**
- `edges` array length = 10
- `pageInfo.hasNextPage` is true (if more than 10 products exist)
- `pageInfo.totalCount` remains consistent with Step 1
- All products have state `AVAILABLE`

### Step 3: Query Second Page Using Cursor
**Action:** Using `endCursor` from Step 2, execute:
```graphql
query {
  products(first: 10, after: "<endCursor_from_step2>") {
    edges {
      node {
        id
        name
        pricePerUnit
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns successfully
- Returns next 10 products (different from Step 2)
- Cursor pagination works correctly

**Validation:**
- `edges` array length = 10 (or fewer if near end)
- All product IDs are different from Step 2
- No duplicate products between pages
- `pageInfo.hasPreviousPage` is true
- `pageInfo.totalCount` remains consistent
- `pageInfo.startCursor` equals `after` parameter passed

### Step 4: Query Large Page Size
**Action:** Execute query with large page size:
```graphql
query {
  products(first: 100) {
    edges {
      node {
        id
        name
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns successfully
- Returns up to 100 products
- Works efficiently

**Validation:**
- `edges` array length ≤ 100
- If `totalCount` > 100, then `pageInfo.hasNextPage` is true
- If `totalCount` ≤ 100, then `edges` length = `totalCount`
- Response time is acceptable (< 2 seconds)

### Step 5: Query with Zero or Negative Page Size
**Action:** Execute query with invalid page size:
```graphql
query {
  products(first: 0) {
    edges {
      node { id }
    }
  }
}
```

**Expected Result:**
- Query returns error or empty result
- Error message indicates invalid page size

**Validation:**
- HTTP status 200 or 400
- Error response includes descriptive message
- Or returns empty edges array with totalCount > 0

### Step 6: Query Last Page (End of Results)
**Action:** Continue pagination until reaching the last page by repeatedly using `endCursor`:
```graphql
query {
  products(first: 20, after: "<cursor_near_end>") {
    edges {
      node {
        id
        name
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns successfully
- Returns remaining products (may be less than 20)
- `hasNextPage` is false

**Validation:**
- `edges` array length ≤ 20
- `pageInfo.hasNextPage` = false
- `pageInfo.hasPreviousPage` = true
- Sum of all products across all pages = `pageInfo.totalCount`

### Step 7: Verify OFF_SHELF Products Excluded
**Action:** Check that products with state `OFF_SHELF` do not appear in results.

**Setup:** 
- Identify or create products with state `OFF_SHELF` in database
- Note their IDs

**Action:** Execute query:
```graphql
query {
  products(first: 100) {
    edges {
      node {
        id
        state
      }
    }
  }
}
```

**Expected Result:**
- No products with state `OFF_SHELF` appear in results
- Only `AVAILABLE` products returned

**Validation:**
- Scan all returned product IDs
- Verify none match the OFF_SHELF product IDs
- All `node.state` values = `AVAILABLE`

### Step 8: Verify Out-of-Stock Products Excluded
**Action:** Check that products with `countInStock = 0` do not appear in results.

**Setup:** 
- Identify or create products with `countInStock = 0` in database

**Action:** Execute query:
```graphql
query {
  products(first: 100) {
    edges {
      node {
        id
        countInStock
      }
    }
  }
}
```

**Expected Result:**
- No products with `countInStock = 0` appear in results
- Only in-stock products returned

**Validation:**
- All `node.countInStock` > 0

### Step 9: Verify Product Field Data Integrity
**Action:** Query detailed product information and validate data quality:
```graphql
query {
  products(first: 5) {
    edges {
      node {
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
  }
}
```

**Expected Result:**
- All fields have appropriate data types
- Timestamps are valid ISO 8601 format
- Image data (if present) follows data URI scheme

**Validation:**
- `id` is non-empty string
- `name` is non-empty string
- `description` can be null or non-empty string
- `imageData` is null or starts with "data:image/"
- `pricePerUnit` > 0 (positive integer)
- `countInStock` ≥ 1 (positive integer)
- `state` = "AVAILABLE"
- `createdAt` is valid ISO 8601 timestamp
- `updatedAt` is valid ISO 8601 timestamp
- `updatedAt` ≥ `createdAt`

### Step 10: Verify Cursor Consistency
**Action:** Query the same page multiple times and verify consistent results:
```graphql
query {
  products(first: 10) {
    edges {
      node { id }
      cursor
    }
    pageInfo {
      endCursor
      totalCount
    }
  }
}
```

**Expected Result:**
- Multiple queries return identical results (assuming no data changes)
- Cursors remain consistent

**Validation:**
- Product IDs match across repeated queries
- Cursors match across repeated queries
- `totalCount` remains consistent
- Order of products is deterministic

## Success Criteria
- ✅ Products query returns only AVAILABLE products with stock
- ✅ Pagination works correctly with `first` and `after` parameters
- ✅ Page info accurately reflects pagination state
- ✅ Cursors enable traversal through all pages
- ✅ No duplicate products across pages
- ✅ All product fields have valid data types and values
- ✅ OFF_SHELF and out-of-stock products are excluded
- ✅ Query handles edge cases (invalid page size, last page)
- ✅ Results are consistent and deterministic
- ✅ Performance is acceptable for reasonable page sizes

## Notes
- This query is used by the customer landing page to display products
- Only products suitable for purchase should be returned
- Default page size is 20 if not specified
- Cursor-based pagination ensures consistent results even with data updates
