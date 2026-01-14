# API-TC004: Customer Place Order

## Summary
Verify that customers can successfully place orders from their shopping cart through the GraphQL `placeOrder` mutation.

## Description
This test case validates the order placement process including customer information validation (name, email, shipping address), order creation from cart contents, cart clearing after successful order, order state initialization, and proper error handling. It tests the complete checkout flow from cart to confirmed order.

## Prerequisites
- Frontend service is running and GraphQL endpoint is accessible
- Transaction service is running with Cart and Order services
- Database contains products with state AVAILABLE and sufficient stock
- Fresh session with empty cart

## Test Steps

### Step 1: Place Order with Valid Information
**Setup:** 
1. Add 2-3 products to cart with various quantities
2. Verify cart has items and total price > 0

**Action:** Execute placeOrder mutation:
```graphql
mutation {
  placeOrder(input: {
    customerName: "John Doe"
    customerEmail: "john.doe@example.com"
    shippingAddress: "123 Main St, Apt 4B, New York, NY 10001"
  }) {
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
}
```

**Expected Result:**
- Order created successfully
- Order contains all cart items
- Cart is cleared
- Order state is PROCESSING

**Validation:**
- `order.id` is non-empty unique string
- `order.customerName` = "John Doe"
- `order.customerEmail` = "john.doe@example.com"
- `order.shippingAddress` = "123 Main St, Apt 4B, New York, NY 10001"
- `order.items.length` matches cart items count
- Each `order.items[].product` matches original cart products
- Each `order.items[].quantity` matches cart quantities
- `order.totalPrice` matches cart total price
- `order.state` = "PROCESSING"
- `order.createdAt` is valid ISO 8601 timestamp
- `order.updatedAt` equals `order.createdAt` (newly created)

**Post-Validation:** Query cart to verify it's empty:
```graphql
query {
  cart {
    items {
      product { id }
      quantity
    }
    totalPrice
  }
}
```
- `cart.items.length` = 0
- `cart.totalPrice` = 0

### Step 2: Place Order with Minimal Address
**Setup:** Add products to cart

**Action:** Execute placeOrder with minimal address:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Jane Smith"
    customerEmail: "jane@example.com"
    shippingAddress: "456 Oak Avenue"
  }) {
    id
    customerName
    customerEmail
    shippingAddress
    totalPrice
    state
  }
}
```

**Expected Result:**
- Order created successfully
- Simple address accepted

**Validation:**
- `order.id` is non-empty
- `order.shippingAddress` = "456 Oak Avenue"
- Order created with minimal address
- Cart is cleared

### Step 3: Place Order with Long Customer Name
**Setup:** Add products to cart

**Action:** Execute placeOrder with long name:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Alexander Christopher Wellington Montgomery III"
    customerEmail: "alexander@example.com"
    shippingAddress: "789 Elm Street"
  }) {
    id
    customerName
  }
}
```

**Expected Result:**
- Order created successfully
- Long name handled correctly

**Validation:**
- `order.customerName` = "Alexander Christopher Wellington Montgomery III"
- Full name stored without truncation
- Or appropriate error if name exceeds length limit

### Step 4: Place Order with International Address
**Setup:** Add products to cart

**Action:** Execute placeOrder with international address:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Pierre Dubois"
    customerEmail: "pierre@example.fr"
    shippingAddress: "42 Rue de la Paix, 75002 Paris, France"
  }) {
    id
    shippingAddress
  }
}
```

**Expected Result:**
- Order created successfully
- International address accepted

**Validation:**
- `order.shippingAddress` = "42 Rue de la Paix, 75002 Paris, France"
- Special characters and non-ASCII characters handled

### Step 5: Place Order with Empty Cart
**Setup:** Ensure cart is empty (no items)

**Action:** Execute placeOrder:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Empty Cart User"
    customerEmail: "empty@example.com"
    shippingAddress: "No Items Street"
  }) {
    id
    items {
      product { id }
    }
    totalPrice
  }
}
```

**Expected Result:**
- Mutation returns error
- Cannot place order with empty cart

**Validation:**
- Response contains error
- Error message indicates empty cart or no items
- No order created

### Step 6: Place Order with Missing Customer Name
**Setup:** Add products to cart

**Action:** Execute placeOrder without customerName:
```graphql
mutation {
  placeOrder(input: {
    customerEmail: "nohash@example.com"
    shippingAddress: "999 Test Ave"
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
- Error message indicates missing required field `customerName`
- No order created
- Cart unchanged

### Step 7: Place Order with Empty Customer Name
**Setup:** Add products to cart

**Action:** Execute placeOrder with empty string name:
```graphql
mutation {
  placeOrder(input: {
    customerName: ""
    customerEmail: "empty@example.com"
    shippingAddress: "Empty Name Street"
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Empty name not accepted

**Validation:**
- Response contains error
- Error message indicates invalid or empty customer name
- No order created
- Cart unchanged

### Step 8: Place Order with Missing Email
**Setup:** Add products to cart

**Action:** Execute placeOrder without email:
```graphql
mutation {
  placeOrder(input: {
    customerName: "No Email User"
    shippingAddress: "No Email Street"
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
- Error message indicates missing required field `customerEmail`
- No order created

### Step 9: Place Order with Invalid Email Format
**Setup:** Add products to cart

**Action:** Execute placeOrder with invalid email:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Invalid Email User"
    customerEmail: "not-an-email"
    shippingAddress: "Invalid Email Street"
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Email format validation

**Validation:**
- Response contains error
- Error message indicates invalid email format
- No order created
- Cart unchanged

### Step 10: Place Order with Various Invalid Email Formats
**Setup:** Add products to cart

**Action:** Test multiple invalid email formats:
```graphql
# Missing @ symbol
mutation { placeOrder(input: {customerName: "Test", customerEmail: "invalidemail.com", shippingAddress: "Test St"}) { id } }

# Missing domain
mutation { placeOrder(input: {customerName: "Test", customerEmail: "test@", shippingAddress: "Test St"}) { id } }

# Missing username
mutation { placeOrder(input: {customerName: "Test", customerEmail: "@example.com", shippingAddress: "Test St"}) { id } }

# Multiple @ symbols
mutation { placeOrder(input: {customerName: "Test", customerEmail: "test@@example.com", shippingAddress: "Test St"}) { id } }

# Spaces in email
mutation { placeOrder(input: {customerName: "Test", customerEmail: "test user@example.com", shippingAddress: "Test St"}) { id } }
```

**Expected Result:**
- All mutations return errors
- Email validation catches various invalid formats

**Validation:**
- Each attempt returns error
- Error messages indicate invalid email format
- No orders created
- Cart remains unchanged

### Step 11: Place Order with Valid Email Variations
**Setup:** Add products to cart for each test

**Action:** Test valid email formats:
```graphql
# Standard email
mutation { placeOrder(input: {customerName: "Test1", customerEmail: "user@example.com", shippingAddress: "Test St"}) { id customerEmail } }

# Email with plus sign
mutation { placeOrder(input: {customerName: "Test2", customerEmail: "user+tag@example.com", shippingAddress: "Test St"}) { id customerEmail } }

# Email with dots
mutation { placeOrder(input: {customerName: "Test3", customerEmail: "first.last@example.com", shippingAddress: "Test St"}) { id customerEmail } }

# Email with subdomain
mutation { placeOrder(input: {customerName: "Test4", customerEmail: "user@mail.example.com", shippingAddress: "Test St"}) { id customerEmail } }

# Email with numbers
mutation { placeOrder(input: {customerName: "Test5", customerEmail: "user123@example.com", shippingAddress: "Test St"}) { id customerEmail } }
```

**Expected Result:**
- All mutations succeed
- Various valid email formats accepted

**Validation:**
- Each order created successfully
- Email stored exactly as provided
- Each cart cleared after order

### Step 12: Place Order with Missing Shipping Address
**Setup:** Add products to cart

**Action:** Execute placeOrder without shipping address:
```graphql
mutation {
  placeOrder(input: {
    customerName: "No Address User"
    customerEmail: "noaddress@example.com"
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
- Error message indicates missing required field `shippingAddress`
- No order created

### Step 13: Place Order with Empty Shipping Address
**Setup:** Add products to cart

**Action:** Execute placeOrder with empty address:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Empty Address User"
    customerEmail: "empty@example.com"
    shippingAddress: ""
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Empty address not accepted

**Validation:**
- Response contains error
- Error message indicates invalid or empty shipping address
- No order created

### Step 14: Place Order with Special Characters in Fields
**Setup:** Add products to cart

**Action:** Execute placeOrder with special characters:
```graphql
mutation {
  placeOrder(input: {
    customerName: "O'Brien-Smith & Co."
    customerEmail: "test@example.com"
    shippingAddress: "123 Main St., Apt #4B, <script>alert('xss')</script>"
  }) {
    id
    customerName
    shippingAddress
  }
}
```

**Expected Result:**
- Order created successfully
- Special characters sanitized or escaped properly
- No XSS vulnerabilities

**Validation:**
- Order created
- `order.customerName` preserves legitimate special characters (apostrophe, hyphen, ampersand)
- `order.shippingAddress` sanitizes or escapes HTML/script tags
- No script execution or XSS vulnerability
- Special characters stored safely

### Step 15: Place Order with Unicode Characters
**Setup:** Add products to cart

**Action:** Execute placeOrder with Unicode:
```graphql
mutation {
  placeOrder(input: {
    customerName: "田中太郎"
    customerEmail: "tanaka@example.jp"
    shippingAddress: "東京都渋谷区 1-2-3"
  }) {
    id
    customerName
    shippingAddress
  }
}
```

**Expected Result:**
- Order created successfully
- Unicode characters preserved

**Validation:**
- `order.customerName` = "田中太郎"
- `order.shippingAddress` = "東京都渋谷区 1-2-3"
- Unicode characters stored and retrieved correctly

### Step 16: Place Multiple Orders in Succession
**Setup:** Add products to cart

**Action:** Place first order, then add products and place second order:
```graphql
# First order
mutation {
  placeOrder(input: {
    customerName: "Multi Order User 1"
    customerEmail: "multi1@example.com"
    shippingAddress: "First Address"
  }) {
    id
  }
}

# Add products again
mutation {
  addToCart(input: { productId: "product-001", quantity: 2 }) {
    items { product { id } }
  }
}

# Second order
mutation {
  placeOrder(input: {
    customerName: "Multi Order User 2"
    customerEmail: "multi2@example.com"
    shippingAddress: "Second Address"
  }) {
    id
  }
}
```

**Expected Result:**
- Both orders created successfully
- Each order has unique ID
- Cart cleared after each order

**Validation:**
- First `order.id` ≠ second `order.id`
- Both orders exist in system
- Cart is empty after second order
- Each order independent

### Step 17: Verify Product Snapshot in Order
**Setup:** 
1. Add product to cart (note current price)
2. Place order
3. Update product price in inventory
4. Query the order

**Action:** Query created order:
```graphql
query {
  order(id: "order-id-from-previous-step") {
    id
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
- Order contains product snapshot at time of purchase
- Price in order doesn't change when inventory price changes

**Validation:**
- `order.items[].product.pricePerUnit` matches price at time of order placement
- Price is not affected by subsequent inventory updates
- Product snapshot is immutable

### Step 18: Place Order and Verify Stock Deduction
**Setup:**
1. Query product and note current `countInStock`
2. Add product to cart with quantity X
3. Place order

**Action:** Query product after order:
```graphql
query {
  product(id: "product-id") {
    id
    countInStock
  }
}
```

**Expected Result:**
- Product stock may be decremented (depends on business logic)
- Stock management is consistent

**Validation:**
- If stock management is immediate: `countInStock` = original - X
- If stock management is on fulfillment: `countInStock` unchanged
- Behavior is consistent with documented business logic
- No negative stock values

### Step 19: Place Order with Product Becoming Unavailable
**Setup:**
1. Add product to cart
2. Change product state to OFF_SHELF in database
3. Attempt to place order

**Action:** Execute placeOrder:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Test User"
    customerEmail: "test@example.com"
    shippingAddress: "Test Address"
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Order not created if cart contains unavailable products

**Validation:**
- Response contains error
- Error message indicates product no longer available
- No order created
- Cart may be updated to remove unavailable item

### Step 20: Place Order with Insufficient Stock
**Setup:**
1. Add product to cart with quantity X
2. Reduce product stock to less than X in database
3. Attempt to place order

**Action:** Execute placeOrder:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Test User"
    customerEmail: "test@example.com"
    shippingAddress: "Test Address"
  }) {
    id
  }
}
```

**Expected Result:**
- Mutation returns error
- Order not created due to insufficient stock

**Validation:**
- Response contains error
- Error message indicates insufficient stock
- Shows current available stock
- No order created

### Step 21: Verify Order Total Calculation
**Setup:** Create cart with known items and prices:
- Product A: price 1250, quantity 2 → 2500
- Product B: price 3000, quantity 1 → 3000
- Product C: price 500, quantity 5 → 2500
- Expected total: 8000

**Action:** Execute placeOrder and verify:
```graphql
mutation {
  placeOrder(input: {
    customerName: "Calculation Test"
    customerEmail: "calc@example.com"
    shippingAddress: "Test"
  }) {
    items {
      product { pricePerUnit }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- All calculations accurate
- No rounding errors

**Validation:**
- Item A: `totalPrice` = 2500
- Item B: `totalPrice` = 3000
- Item C: `totalPrice` = 2500
- `order.totalPrice` = 8000
- Prices stored as integers (cents) avoid floating-point errors

### Step 22: Place Order and Verify State
**Action:** Query order immediately after creation:
```graphql
query {
  order(id: "newly-created-order-id") {
    id
    state
    createdAt
    updatedAt
  }
}
```

**Expected Result:**
- Order state is PROCESSING
- Timestamps are consistent

**Validation:**
- `order.state` = "PROCESSING"
- `order.createdAt` is recent timestamp
- `order.updatedAt` equals `order.createdAt`
- Not in SHIPPED, COMPLETED, or CANCELED state

## Success Criteria
- ✅ Order successfully created from cart with valid customer information
- ✅ Cart is automatically cleared after successful order placement
- ✅ Order contains accurate snapshot of cart items at time of purchase
- ✅ Customer name, email, and shipping address are required and validated
- ✅ Email format validation rejects invalid emails
- ✅ Empty or missing fields return appropriate errors
- ✅ Special characters and Unicode handled correctly
- ✅ XSS attempts are sanitized
- ✅ Order state initializes to PROCESSING
- ✅ Order total matches cart total
- ✅ Product snapshots are immutable (prices don't change)
- ✅ Multiple orders can be placed in succession
- ✅ Unavailable or out-of-stock products prevent order creation
- ✅ Order receives unique ID
- ✅ Timestamps are accurate and consistent
- ✅ No integer overflow in price calculations

## Notes
- This mutation completes the customer purchase flow
- Cart must have items before placing order
- Product availability should be validated at order time
- Product snapshots in orders preserve state at purchase time
- Order total may include future discounts/promotions (not in current scope)
- Email validation should follow RFC 5322 standards
- Shipping address validation depends on business requirements
- Stock deduction timing (immediate vs. on fulfillment) is business logic dependent
