# API-TC005: Admin Query Products with Filters

## Summary
Verify that administrators can query all products in the inventory with pagination and various filters through the GraphQL admin `products` query.

## Description
This test case validates the admin-facing `products` query which returns a paginated list of all products in the inventory, including OFF_SHELF and deleted products. Unlike the customer query, this includes all product states and supports filtering by state and search by name. It tests pagination, filtering combinations, and search functionality.

## Prerequisites
- Frontend service is running and admin GraphQL endpoint is accessible
- Admin authentication/authorization in place (if implemented)
- Database contains at least 50 products in various states (AVAILABLE, OFF_SHELF)
- Products have varied names for search testing

## Test Steps

### Step 1: Query All Products (No Filters)
**Action:** Execute admin GraphQL query:
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
- Returns 20 products (default page size)
- Includes products in ALL states (AVAILABLE, OFF_SHELF)

**Validation:**
- `edges` array length = 20 (or fewer if total < 20)
- Products include both AVAILABLE and OFF_SHELF states
- Each `node` has all fields populated
- `pageInfo.totalCount` includes all products (not just AVAILABLE)
- `pageInfo.hasNextPage` reflects if more products exist
- All cursors are unique and non-empty

### Step 2: Filter by AVAILABLE State
**Action:** Execute query with state filter:
```graphql
query {
  products(
    first: 50
    filter: {
      state: AVAILABLE
    }
  ) {
    edges {
      node {
        id
        name
        state
      }
      cursor
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns only AVAILABLE products
- Total count reflects only AVAILABLE products

**Validation:**
- All `node.state` = "AVAILABLE"
- No OFF_SHELF products in results
- `pageInfo.totalCount` = count of AVAILABLE products only
- Count is less than or equal to total products from Step 1

### Step 3: Filter by OFF_SHELF State
**Action:** Execute query with OFF_SHELF filter:
```graphql
query {
  products(
    first: 50
    filter: {
      state: OFF_SHELF
    }
  ) {
    edges {
      node {
        id
        name
        state
      }
      cursor
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns only OFF_SHELF products
- Total count reflects only OFF_SHELF products

**Validation:**
- All `node.state` = "OFF_SHELF"
- No AVAILABLE products in results
- `pageInfo.totalCount` = count of OFF_SHELF products only
- Sum of AVAILABLE (Step 2) + OFF_SHELF (Step 3) counts ≤ total (Step 1)

### Step 4: Search Products by Name
**Action:** Execute query with name search:
```graphql
query {
  products(
    first: 50
    filter: {
      searchName: "laptop"
    }
  ) {
    edges {
      node {
        id
        name
        state
      }
      cursor
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns products with "laptop" in name
- Case-insensitive partial match
- Includes all matching products regardless of state

**Validation:**
- Each `node.name` contains "laptop" (case-insensitive)
- Search is case-insensitive ("Laptop", "LAPTOP", "laptop" all match)
- Partial matches included ("Gaming Laptop", "Laptop Bag")
- `pageInfo.totalCount` reflects matching products
- Both AVAILABLE and OFF_SHELF products included if they match

### Step 5: Search with No Matches
**Action:** Execute query with search term that matches no products:
```graphql
query {
  products(
    filter: {
      searchName: "xyznonexistentproduct123"
    }
  ) {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns successfully
- Empty results
- Total count is zero

**Validation:**
- `edges` array is empty (length = 0)
- `pageInfo.totalCount` = 0
- No error returned (empty result is valid)

### Step 6: Combine State Filter and Name Search
**Action:** Execute query with both filters:
```graphql
query {
  products(
    first: 50
    filter: {
      state: AVAILABLE
      searchName: "phone"
    }
  ) {
    edges {
      node {
        id
        name
        state
      }
      cursor
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns products that match BOTH conditions
- Only AVAILABLE products with "phone" in name

**Validation:**
- All `node.state` = "AVAILABLE"
- All `node.name` contain "phone" (case-insensitive)
- `pageInfo.totalCount` ≤ counts from either filter alone
- Results are intersection of both filters

### Step 7: Pagination with Filters
**Action:** Execute filtered query with pagination:
```graphql
query {
  products(
    first: 10
    filter: {
      state: AVAILABLE
    }
  ) {
    edges {
      node {
        id
        name
        state
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
      totalCount
    }
  }
}
```

**Then use cursor for next page:**
```graphql
query {
  products(
    first: 10
    after: "<endCursor_from_previous>"
    filter: {
      state: AVAILABLE
    }
  ) {
    edges {
      node {
        id
        name
        state
      }
    }
    pageInfo {
      hasPreviousPage
      totalCount
    }
  }
}
```

**Expected Result:**
- Pagination works correctly with filters applied
- Filter persists across pages
- No duplicate products between pages

**Validation:**
- First page returns 10 AVAILABLE products
- Second page returns next 10 AVAILABLE products
- All products across both pages have state AVAILABLE
- No duplicate product IDs between pages
- `pageInfo.totalCount` consistent across both queries
- `pageInfo.hasPreviousPage` = true on second page

### Step 8: Query with Custom Page Size
**Action:** Execute query with various page sizes:
```graphql
query {
  products(first: 10) {
    edges { node { id } }
    pageInfo { totalCount }
  }
}

query {
  products(first: 50) {
    edges { node { id } }
    pageInfo { totalCount }
  }
}

query {
  products(first: 100) {
    edges { node { id } }
    pageInfo { totalCount }
  }
}
```

**Expected Result:**
- Each query returns requested number of products
- Total count remains consistent

**Validation:**
- First query: `edges.length` = 10 (or fewer if total < 10)
- Second query: `edges.length` = 50 (or fewer if total < 50)
- Third query: `edges.length` = 100 (or fewer if total < 100)
- `pageInfo.totalCount` is same across all queries

### Step 9: Search with Partial Name Match
**Action:** Execute searches with partial terms:
```graphql
# Search for "gam" should match "Gaming Laptop", "Board Game", etc.
query {
  products(filter: { searchName: "gam" }) {
    edges {
      node {
        id
        name
      }
    }
  }
}

# Search for "pro" should match "MacBook Pro", "Product", "Professional", etc.
query {
  products(filter: { searchName: "pro" }) {
    edges {
      node {
        id
        name
      }
    }
  }
}
```

**Expected Result:**
- Partial matches work correctly
- All products containing the substring returned

**Validation:**
- All returned products contain search term as substring
- Case-insensitive matching
- Matches at any position in name (start, middle, end)

### Step 10: Search with Special Characters
**Action:** Execute search with special characters:
```graphql
query {
  products(filter: { searchName: "O'Brien" }) {
    edges {
      node {
        id
        name
      }
    }
  }
}

query {
  products(filter: { searchName: "20\"" }) {
    edges {
      node {
        id
        name
      }
    }
  }
}
```

**Expected Result:**
- Special characters handled safely
- No SQL injection or errors

**Validation:**
- Query executes without errors
- Returns matching products if they exist
- Special characters escaped/handled properly
- No system errors or SQL injection

### Step 11: Query Products Including Out-of-Stock
**Action:** Execute query without stock filter:
```graphql
query {
  products(first: 50) {
    edges {
      node {
        id
        name
        countInStock
        state
      }
    }
  }
}
```

**Expected Result:**
- Query returns products with ANY stock level
- Includes products with countInStock = 0
- Unlike customer query, shows out-of-stock items

**Validation:**
- Some products may have `countInStock` = 0
- Products with zero stock are included
- Admin can see all inventory regardless of stock

### Step 12: Verify All Product Fields Available
**Action:** Query all fields to verify completeness:
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
- All product fields accessible
- Optional fields can be null

**Validation:**
- `id` is non-empty string
- `name` is non-empty string
- `description` is string or null
- `imageData` is string or null
- `pricePerUnit` is positive integer
- `countInStock` is non-negative integer
- `state` is valid enum (AVAILABLE or OFF_SHELF)
- `createdAt` and `updatedAt` are valid timestamps
- `updatedAt` ≥ `createdAt`

### Step 13: Query Products Ordered by Creation Date
**Action:** Query multiple pages and verify order:
```graphql
query {
  products(first: 20) {
    edges {
      node {
        id
        name
        createdAt
      }
      cursor
    }
  }
}
```

**Expected Result:**
- Products returned in consistent order
- Order is deterministic (likely by creation date or ID)

**Validation:**
- Products returned in same order on repeated queries
- Order is deterministic and consistent
- Newer products may appear first or last depending on sorting

### Step 14: Search Case Sensitivity Verification
**Action:** Execute searches with different cases:
```graphql
query {
  products(filter: { searchName: "laptop" }) {
    edges { node { id name } }
    pageInfo { totalCount }
  }
}

query {
  products(filter: { searchName: "LAPTOP" }) {
    edges { node { id name } }
    pageInfo { totalCount }
  }
}

query {
  products(filter: { searchName: "LaPtOp" }) {
    edges { node { id name } }
    pageInfo { totalCount }
  }
}
```

**Expected Result:**
- All three queries return identical results
- Search is case-insensitive

**Validation:**
- All three queries return same product IDs
- `pageInfo.totalCount` identical across all queries
- Case of search term doesn't affect results

### Step 15: Empty Filter Object
**Action:** Execute query with empty filter:
```graphql
query {
  products(
    first: 20
    filter: {}
  ) {
    edges {
      node {
        id
        name
        state
      }
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns all products
- Empty filter equals no filter

**Validation:**
- Results same as query without filter (Step 1)
- All states included
- `pageInfo.totalCount` matches unfiltered query

### Step 16: Query with Null Filter
**Action:** Execute query with null filter:
```graphql
query {
  products(
    first: 20
    filter: null
  ) {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns all products or same as empty filter
- Null filter handled gracefully

**Validation:**
- Query succeeds
- Results match unfiltered query
- No errors

### Step 17: Verify Cursor Stability with Filters
**Action:** Execute same filtered query multiple times:
```graphql
query {
  products(
    first: 10
    filter: { state: AVAILABLE }
  ) {
    edges {
      node { id }
      cursor
    }
    pageInfo {
      endCursor
    }
  }
}
```

**Expected Result:**
- Cursors are consistent across repeated queries
- Same products return same cursors

**Validation:**
- Product IDs match across repeated queries
- Cursors match across repeated queries
- Results are deterministic and stable

### Step 18: Large Page Size with Filters
**Action:** Execute query with large page size and filter:
```graphql
query {
  products(
    first: 200
    filter: { state: AVAILABLE }
  ) {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query handles large page size
- Performance is acceptable
- All filtered results returned

**Validation:**
- `edges.length` ≤ 200
- All returned products have state AVAILABLE
- Response time < 3 seconds
- Memory usage reasonable

### Step 19: Search with Empty String
**Action:** Execute query with empty search term:
```graphql
query {
  products(
    filter: {
      searchName: ""
    }
  ) {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Empty search returns all products or no products
- Handled consistently

**Validation:**
- Query succeeds without error
- Either returns all products (empty search ignored)
- Or returns no products (empty search matches nothing)
- Behavior is consistent and documented

### Step 20: Verify Filter Doesn't Affect Other Queries
**Action:** Execute filtered and unfiltered queries in parallel sessions:
```graphql
# Session 1: Filtered query
query {
  products(filter: { state: AVAILABLE }) {
    pageInfo { totalCount }
  }
}

# Session 2: Unfiltered query
query {
  products {
    pageInfo { totalCount }
  }
}
```

**Expected Result:**
- Filters are session/query specific
- One query doesn't affect another

**Validation:**
- Filtered query totalCount ≤ unfiltered totalCount
- Both queries return correct results
- No cross-contamination between queries

## Success Criteria
- ✅ Admin query returns ALL products including OFF_SHELF
- ✅ State filter correctly filters by AVAILABLE or OFF_SHELF
- ✅ Name search performs case-insensitive partial matching
- ✅ Filters can be combined (state + search)
- ✅ Pagination works correctly with filters applied
- ✅ Empty/null filters return all products
- ✅ Special characters in search handled safely
- ✅ Out-of-stock products included in results
- ✅ All product fields accessible
- ✅ Cursors are stable and consistent
- ✅ Large page sizes perform acceptably
- ✅ Search is truly case-insensitive
- ✅ Results are deterministic and repeatable
- ✅ No SQL injection vulnerabilities

## Notes
- Admin query differs from customer query by including ALL product states
- Admins need to see OFF_SHELF and out-of-stock products for inventory management
- State filter is optional; without it, all states are returned
- Name search is case-insensitive substring match
- Multiple filters are combined with AND logic
- Default page size is 20 if not specified
- This query is used by the admin inventory management page
