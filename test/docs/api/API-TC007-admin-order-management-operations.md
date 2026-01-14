# API-TC007: Admin Order Management Operations

## Summary
Verify that administrators can query orders with filters and update order states through GraphQL API.

## Description
This test case validates admin order management operations including querying orders with pagination and filters, viewing order details, and updating order states through the valid state transitions (PROCESSING → SHIPPED → COMPLETED, and cancellation from PROCESSING or SHIPPED states). It tests state machine enforcement, error handling for invalid transitions, and data integrity.

## Prerequisites
- Frontend service is running and admin GraphQL endpoint is accessible
- Admin authentication/authorization in place (if implemented)
- Transaction service is running with Order service
- Database contains at least 30 orders in various states:
  - 10 in PROCESSING state
  - 8 in SHIPPED state
  - 10 in COMPLETED state
  - 2 in CANCELED state
- Orders have different customer emails and dates

## Test Steps

### Step 1: Query All Orders (No Filters)
**Action:** Execute admin GraphQL query for orders:
```graphql
query {
  orders {
    edges {
      node {
        id
        customerName
        customerEmail
        shippingAddress
        items {
          product {
            id
            name
            pricePerUnit
          }
          quantity
          totalPrice
        }
        totalPrice
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
- Returns 20 orders (default page size)
- Includes orders in all states

**Validation:**
- `edges` array length = 20 (or fewer if total < 20)
- Orders include PROCESSING, SHIPPED, COMPLETED, CANCELED states
- Each order has all required fields
- `pageInfo.totalCount` includes all orders
- All cursors are unique and non-empty

### Step 2: Filter Orders by PROCESSING State
**Action:** Execute query with state filter:
```graphql
query {
  orders(
    first: 50
    filter: {
      state: PROCESSING
    }
  ) {
    edges {
      node {
        id
        customerName
        customerEmail
        state
        totalPrice
        createdAt
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
- Query returns only PROCESSING orders
- Total count reflects only PROCESSING orders

**Validation:**
- All `node.state` = "PROCESSING"
- No orders with other states in results
- `pageInfo.totalCount` = count of PROCESSING orders only

### Step 3: Filter Orders by SHIPPED State
**Action:** Execute query with SHIPPED filter:
```graphql
query {
  orders(
    first: 50
    filter: {
      state: SHIPPED
    }
  ) {
    edges {
      node {
        id
        state
        createdAt
      }
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns only SHIPPED orders
- Total count reflects only SHIPPED orders

**Validation:**
- All `node.state` = "SHIPPED"
- `pageInfo.totalCount` = count of SHIPPED orders

### Step 4: Filter Orders by COMPLETED State
**Action:** Execute query with COMPLETED filter:
```graphql
query {
  orders(
    filter: {
      state: COMPLETED
    }
  ) {
    edges {
      node {
        id
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
- Query returns only COMPLETED orders

**Validation:**
- All `node.state` = "COMPLETED"
- `pageInfo.totalCount` = count of COMPLETED orders

### Step 5: Filter Orders by CANCELED State
**Action:** Execute query with CANCELED filter:
```graphql
query {
  orders(
    filter: {
      state: CANCELED
    }
  ) {
    edges {
      node {
        id
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
- Query returns only CANCELED orders

**Validation:**
- All `node.state` = "CANCELED"
- `pageInfo.totalCount` = count of CANCELED orders

### Step 6: Filter Orders by Customer Email
**Action:** Execute query with email filter:
```graphql
query {
  orders(
    filter: {
      customerEmail: "john.doe@example.com"
    }
  ) {
    edges {
      node {
        id
        customerEmail
        customerName
        state
        totalPrice
      }
    }
    pageInfo {
      totalCount
    }
  }
}
```

**Expected Result:**
- Query returns only orders for specified email
- Multiple orders for same customer returned

**Validation:**
- All `node.customerEmail` = "john.doe@example.com"
- Can include orders in various states
- `pageInfo.totalCount` = count of orders for this email

### Step 7: Combine State and Email Filters
**Action:** Execute query with both filters:
```graphql
query {
  orders(
    filter: {
      state: PROCESSING
      customerEmail: "jane@example.com"
    }
  ) {
    edges {
      node {
        id
        customerEmail
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
- Query returns orders matching both conditions
- Only PROCESSING orders for specified email

**Validation:**
- All `node.state` = "PROCESSING"
- All `node.customerEmail` = "jane@example.com"
- Results are intersection of both filters

### Step 8: Query Single Order by ID
**Action:** Execute query for specific order:
```graphql
query {
  order(id: "<order-id>") {
    id
    customerName
    customerEmail
    shippingAddress
    items {
      product {
        id
        name
        description
        pricePerUnit
      }
      quantity
      totalPrice
    }
    totalPrice
    state
    createdAt
    updatedAt
  }
}
```

**Expected Result:**
- Query returns order details
- All fields populated

**Validation:**
- `id` matches requested order ID
- `customerName`, `customerEmail`, `shippingAddress` are non-empty
- `items` array contains order items
- Each item has product snapshot, quantity, totalPrice
- `totalPrice` = sum of all item totals
- `state` is valid enum value
- `createdAt` and `updatedAt` are valid timestamps

### Step 9: Query Non-Existent Order
**Action:** Execute query with invalid order ID:
```graphql
query {
  order(id: "non-existent-order-999") {
    id
    customerName
  }
}
```

**Expected Result:**
- Query returns null
- No error thrown

**Validation:**
- `order` is null
- No system errors

### Step 10: Ship Order (PROCESSING → SHIPPED)
**Setup:** Identify an order in PROCESSING state

**Action:** Execute shipOrder mutation:
```graphql
mutation {
  shipOrder(id: "<processing-order-id>") {
    id
    state
    updatedAt
    createdAt
  }
}
```

**Expected Result:**
- Order state changed to SHIPPED
- updatedAt timestamp updated

**Validation:**
- `state` = "SHIPPED" (was PROCESSING)
- `updatedAt` > `createdAt`
- `updatedAt` > previous updatedAt value
- `id` unchanged

### Step 11: Complete Order (SHIPPED → COMPLETED)
**Setup:** Use order from Step 10 or identify SHIPPED order

**Action:** Execute completeOrder mutation:
```graphql
mutation {
  completeOrder(id: "<shipped-order-id>") {
    id
    state
    updatedAt
  }
}
```

**Expected Result:**
- Order state changed to COMPLETED
- updatedAt timestamp updated

**Validation:**
- `state` = "COMPLETED" (was SHIPPED)
- `updatedAt` reflects latest update
- State transition successful

### Step 12: Cancel Order from PROCESSING State
**Setup:** Identify an order in PROCESSING state

**Action:** Execute cancelOrder mutation:
```graphql
mutation {
  cancelOrder(id: "<processing-order-id>") {
    id
    state
    updatedAt
  }
}
```

**Expected Result:**
- Order state changed to CANCELED
- Cancellation from PROCESSING allowed

**Validation:**
- `state` = "CANCELED" (was PROCESSING)
- `updatedAt` reflects cancellation time
- State transition successful

### Step 13: Cancel Order from SHIPPED State
**Setup:** Identify an order in SHIPPED state

**Action:** Execute cancelOrder mutation:
```graphql
mutation {
  cancelOrder(id: "<shipped-order-id>") {
    id
    state
    updatedAt
  }
}
```

**Expected Result:**
- Order state changed to CANCELED
- Cancellation from SHIPPED allowed

**Validation:**
- `state` = "CANCELED" (was SHIPPED)
- State transition successful
- Order can be canceled even after shipping

### Step 14: Try to Ship Already SHIPPED Order
**Setup:** Use order that is already SHIPPED

**Action:** Execute shipOrder mutation:
```graphql
mutation {
  shipOrder(id: "<already-shipped-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Mutation returns error
- Invalid state transition

**Validation:**
- Response contains error
- Error message indicates invalid state transition
- Order state unchanged (remains SHIPPED)

### Step 15: Try to Complete Order from PROCESSING State
**Setup:** Identify order in PROCESSING state

**Action:** Execute completeOrder mutation:
```graphql
mutation {
  completeOrder(id: "<processing-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Mutation returns error
- Invalid state transition (must ship first)

**Validation:**
- Response contains error
- Error message indicates invalid transition
- Order state unchanged (remains PROCESSING)
- Proper state machine enforcement

### Step 16: Try to Ship Already COMPLETED Order
**Setup:** Use order in COMPLETED state

**Action:** Execute shipOrder mutation:
```graphql
mutation {
  shipOrder(id: "<completed-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Mutation returns error
- Cannot change COMPLETED order

**Validation:**
- Response contains error
- Order state unchanged (remains COMPLETED)
- COMPLETED is terminal state

### Step 17: Try to Cancel Already COMPLETED Order
**Setup:** Use order in COMPLETED state

**Action:** Execute cancelOrder mutation:
```graphql
mutation {
  cancelOrder(id: "<completed-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Mutation returns error
- Cannot cancel completed order

**Validation:**
- Response contains error
- Error message indicates invalid transition
- Order state unchanged (remains COMPLETED)

### Step 18: Try to Ship CANCELED Order
**Setup:** Use order in CANCELED state

**Action:** Execute shipOrder mutation:
```graphql
mutation {
  shipOrder(id: "<canceled-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Mutation returns error
- Cannot ship canceled order

**Validation:**
- Response contains error
- Order state unchanged (remains CANCELED)
- CANCELED is terminal state

### Step 19: Try to Complete CANCELED Order
**Setup:** Use order in CANCELED state

**Action:** Execute completeOrder mutation:
```graphql
mutation {
  completeOrder(id: "<canceled-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Mutation returns error
- Cannot complete canceled order

**Validation:**
- Response contains error
- Order state unchanged (remains CANCELED)

### Step 20: Try to Cancel Already CANCELED Order
**Setup:** Use order in CANCELED state

**Action:** Execute cancelOrder mutation:
```graphql
mutation {
  cancelOrder(id: "<canceled-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Mutation succeeds (idempotent) or returns error
- Order remains canceled

**Validation:**
- Order `state` = "CANCELED"
- Either succeeds (no-op) or returns error
- Behavior is consistent

### Step 21: Verify Valid State Transition Sequence
**Setup:** Create new order (should be in PROCESSING state)

**Action:** Execute state transitions in valid sequence:
```graphql
# Ship the order
mutation {
  shipOrder(id: "<new-order-id>") {
    id
    state
  }
}

# Complete the order
mutation {
  completeOrder(id: "<new-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Both transitions succeed
- Order moves through proper lifecycle

**Validation:**
- After ship: `state` = "SHIPPED"
- After complete: `state` = "COMPLETED"
- Valid lifecycle: PROCESSING → SHIPPED → COMPLETED

### Step 22: Verify Alternate State Transition Sequence with Cancel
**Setup:** Create new order in PROCESSING state

**Action:** Execute cancellation:
```graphql
mutation {
  cancelOrder(id: "<new-order-id>") {
    id
    state
  }
}
```

**Expected Result:**
- Order transitions to CANCELED
- Valid alternate lifecycle

**Validation:**
- `state` = "CANCELED"
- Valid lifecycle: PROCESSING → CANCELED

### Step 23: Update Order State via Generic Update (if available)
**Action:** Try to use updateOrder mutation (if exists) to change state:
```graphql
mutation {
  updateOrder(input: {
    id: "<processing-order-id>"
    state: SHIPPED
  }) {
    id
    state
  }
}
```

**Expected Result:**
- Mutation works as alternative to specific mutations
- Or not exposed in GraphQL (only specific mutations available)

**Validation:**
- If mutation exists: state updated correctly
- If not: use dedicated mutations (ship, complete, cancel)
- State machine rules still enforced

### Step 24: Verify Order Items Immutability
**Setup:** Query order and note item details

**Action:** 
1. Update product price in inventory
2. Query the order again

```graphql
query {
  order(id: "<order-id>") {
    items {
      product {
        id
        name
        pricePerUnit
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- Order items remain unchanged
- Product snapshots are immutable

**Validation:**
- `items[].product.pricePerUnit` matches original order price
- Not affected by inventory price changes
- `totalPrice` unchanged
- Order items are snapshots at time of creation

### Step 25: Verify Order Total Price Accuracy
**Action:** Query order and verify total calculation:
```graphql
query {
  order(id: "<order-id>") {
    items {
      product {
        pricePerUnit
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- Total price matches sum of item totals
- Calculations are accurate

**Validation:**
- Each `items[].totalPrice` = `product.pricePerUnit` × `quantity`
- `order.totalPrice` = Σ(`items[].totalPrice`)
- No rounding errors

### Step 26: Pagination with Order Filters
**Action:** Execute filtered query with pagination:
```graphql
query {
  orders(
    first: 5
    filter: { state: PROCESSING }
  ) {
    edges {
      node {
        id
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

# Then next page
query {
  orders(
    first: 5
    after: "<endCursor_from_previous>"
    filter: { state: PROCESSING }
  ) {
    edges {
      node {
        id
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
- Pagination works with filters
- Filter persists across pages
- No duplicates

**Validation:**
- First page returns 5 PROCESSING orders
- Second page returns next 5 PROCESSING orders
- All orders across both pages have state PROCESSING
- No duplicate order IDs
- `totalCount` consistent across queries

### Step 27: Query Orders Ordered by Date
**Action:** Query orders and verify ordering:
```graphql
query {
  orders(first: 10) {
    edges {
      node {
        id
        createdAt
      }
    }
  }
}
```

**Expected Result:**
- Orders returned in consistent order
- Likely by creation date (newest or oldest first)

**Validation:**
- Order is deterministic and consistent
- Repeated queries return same order
- Ordering makes sense (by date, ID, etc.)

### Step 28: Filter by Partial Email Match
**Action:** Execute query with partial email:
```graphql
query {
  orders(filter: { customerEmail: "example.com" }) {
    edges {
      node {
        id
        customerEmail
      }
    }
  }
}
```

**Expected Result:**
- Behavior depends on filter implementation
- Either exact match only or partial match

**Validation:**
- If exact match: no results or only exact email match
- If partial match: all emails containing "example.com"
- Behavior is consistent and documented

### Step 29: Try State Mutations on Non-Existent Order
**Action:** Execute state mutations with invalid order ID:
```graphql
mutation {
  shipOrder(id: "non-existent-order-999") {
    id
  }
}

mutation {
  completeOrder(id: "non-existent-order-999") {
    id
  }
}

mutation {
  cancelOrder(id: "non-existent-order-999") {
    id
  }
}
```

**Expected Result:**
- All mutations return errors
- Order not found

**Validation:**
- Each response contains error
- Error messages indicate order not found
- No system errors or crashes

### Step 30: Verify updatedAt Changes on State Transitions
**Action:** 
1. Query order and note updatedAt
2. Change state (e.g., ship order)
3. Query again and compare

```graphql
query {
  order(id: "<order-id>") {
    id
    state
    updatedAt
  }
}

mutation {
  shipOrder(id: "<order-id>") {
    id
    state
    updatedAt
  }
}

query {
  order(id: "<order-id>") {
    id
    state
    updatedAt
  }
}
```

**Expected Result:**
- updatedAt timestamp changes on state update
- createdAt never changes

**Validation:**
- `updatedAt` after mutation > `updatedAt` before
- State reflects new value
- `createdAt` unchanged

## Success Criteria
- ✅ Orders query returns all orders with proper pagination
- ✅ State filter correctly filters by order state
- ✅ Email filter returns orders for specific customer
- ✅ Filters can be combined (state + email)
- ✅ Single order query returns complete order details
- ✅ Valid state transitions succeed (PROCESSING→SHIPPED→COMPLETED)
- ✅ Cancel works from PROCESSING and SHIPPED states
- ✅ Invalid state transitions return errors and are rejected
- ✅ Terminal states (COMPLETED, CANCELED) cannot be changed
- ✅ State machine rules strictly enforced
- ✅ Order items are immutable product snapshots
- ✅ Order totals are accurate and unchanging
- ✅ updatedAt timestamp reflects latest state change
- ✅ Non-existent orders return appropriate errors
- ✅ Pagination works with filters applied
- ✅ Results are deterministic and consistent

## Notes
- Valid state transitions:
  - PROCESSING → SHIPPED (shipOrder)
  - SHIPPED → COMPLETED (completeOrder)
  - PROCESSING → CANCELED (cancelOrder)
  - SHIPPED → CANCELED (cancelOrder)
- Invalid transitions:
  - PROCESSING → COMPLETED (must ship first)
  - Any transition from COMPLETED
  - Any transition from CANCELED (except cancel again, which is no-op)
- Order items contain product snapshots at time of order creation
- Product snapshots are immutable (prices don't change)
- updatedAt timestamp reflects latest state change
- createdAt timestamp never changes
- Order total price includes all items, may include future discounts/promotions
- Email filter match behavior (exact vs. partial) should be documented
