# API-TC003: Customer Cart Query and Mutations

## Summary
Verify that customers can query their shopping cart and perform cart operations (add, update, remove, clear) through GraphQL API.

## Description
This test case validates all customer cart operations including querying the cart, adding products with various quantities, updating item quantities, removing items, and clearing the cart. It tests cart auto-creation, cart ID persistence, quantity management, price calculations, and proper error handling for invalid operations.

## Prerequisites
- Frontend service is running and GraphQL endpoint is accessible
- Transaction service is running with Cart service
- Database contains at least 10 products with state AVAILABLE and countInStock > 5
- Fresh session/context for cart isolation

## Test Steps

### Step 1: Query Cart Before Creation (Auto-Creation)
**Action:** Execute GraphQL query for cart in fresh session:
```graphql
query {
  cart {
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
- Query returns successfully with HTTP 200
- Cart is auto-created with unique ID
- Cart is empty with zero total

**Validation:**
- `cart` is not null
- `cart.id` is non-empty string (UUID or similar format)
- `cart.items` is empty array (length = 0)
- `cart.totalPrice` = 0

### Step 2: Add First Product to Cart
**Action:** Execute addToCart mutation with quantity 1:
```graphql
mutation {
  addToCart(input: {
    productId: "product-001"
    quantity: 1
  }) {
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
- Product is added to cart successfully
- Cart contains one item
- Prices are calculated correctly

**Validation:**
- `cart.id` matches the ID from Step 1
- `cart.items.length` = 1
- `items[0].product.id` = "product-001"
- `items[0].quantity` = 1
- `items[0].totalPrice` = `items[0].product.pricePerUnit` × 1
- `cart.totalPrice` = `items[0].totalPrice`

### Step 3: Add Same Product Again (Increment Quantity)
**Action:** Execute addToCart mutation with same product:
```graphql
mutation {
  addToCart(input: {
    productId: "product-001"
    quantity: 2
  }) {
    id
    items {
      product {
        id
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- Quantity increments for existing item
- No duplicate item created
- Prices updated correctly

**Validation:**
- `cart.items.length` = 1 (still one item)
- `items[0].product.id` = "product-001"
- `items[0].quantity` = 3 (1 + 2)
- `items[0].totalPrice` = `pricePerUnit` × 3
- `cart.totalPrice` = `items[0].totalPrice`

### Step 4: Add Different Product to Cart
**Action:** Execute addToCart mutation with different product:
```graphql
mutation {
  addToCart(input: {
    productId: "product-002"
    quantity: 5
  }) {
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
- Second product is added as new item
- Cart now has two items
- Total price is sum of both items

**Validation:**
- `cart.items.length` = 2
- Item with `product.id` = "product-001" has `quantity` = 3
- Item with `product.id` = "product-002" has `quantity` = 5
- `items[1].totalPrice` = `pricePerUnit` × 5
- `cart.totalPrice` = sum of all `items[].totalPrice`

### Step 5: Update Item Quantity (Increase)
**Action:** Execute updateCartItem mutation to increase quantity:
```graphql
mutation {
  updateCartItem(input: {
    productId: "product-001"
    quantity: 10
  }) {
    id
    items {
      product {
        id
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- Quantity is updated to new value (not incremented)
- Prices recalculated

**Validation:**
- `cart.items.length` = 2
- Item with `product.id` = "product-001" has `quantity` = 10 (not 13)
- `items[0].totalPrice` = `pricePerUnit` × 10
- `cart.totalPrice` updated correctly

### Step 6: Update Item Quantity (Decrease)
**Action:** Execute updateCartItem mutation to decrease quantity:
```graphql
mutation {
  updateCartItem(input: {
    productId: "product-002"
    quantity: 2
  }) {
    id
    items {
      product {
        id
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- Quantity is decreased to new value
- Item still exists in cart
- Prices recalculated

**Validation:**
- `cart.items.length` = 2
- Item with `product.id` = "product-002" has `quantity` = 2
- `items[1].totalPrice` = `pricePerUnit` × 2
- `cart.totalPrice` updated correctly

### Step 7: Update Item Quantity to Zero (Remove Item)
**Action:** Execute updateCartItem mutation with quantity 0:
```graphql
mutation {
  updateCartItem(input: {
    productId: "product-002"
    quantity: 0
  }) {
    id
    items {
      product {
        id
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- Item is removed from cart
- Cart now has one item
- Total price updated

**Validation:**
- `cart.items.length` = 1
- No item with `product.id` = "product-002"
- Only item with `product.id` = "product-001" remains
- `cart.totalPrice` = price of remaining item

### Step 8: Remove Item from Cart
**Action:** Execute removeFromCart mutation:
```graphql
mutation {
  removeFromCart(productId: "product-001") {
    id
    items {
      product {
        id
      }
      quantity
    }
    totalPrice
  }
}
```

**Expected Result:**
- Item is removed from cart
- Cart is now empty
- Total price is zero

**Validation:**
- `cart.items.length` = 0
- `cart.totalPrice` = 0
- `cart.id` remains the same (cart still exists)

### Step 9: Add Multiple Products to Empty Cart
**Action:** Add three different products to cart:
```graphql
mutation AddProduct1 {
  addToCart(input: { productId: "product-003", quantity: 2 }) {
    id
    items { product { id } quantity }
    totalPrice
  }
}

mutation AddProduct2 {
  addToCart(input: { productId: "product-004", quantity: 3 }) {
    id
    items { product { id } quantity }
    totalPrice
  }
}

mutation AddProduct3 {
  addToCart(input: { productId: "product-005", quantity: 1 }) {
    id
    items { product { id } quantity }
    totalPrice
  }
}
```

**Expected Result:**
- All three products added successfully
- Cart has three items
- Total price is sum of all items

**Validation:**
- `cart.items.length` = 3
- Cart contains products 003, 004, 005
- Each item has correct quantity
- `cart.totalPrice` = sum of all individual item totals
- Price calculation: Σ(quantity × pricePerUnit)

### Step 10: Clear Entire Cart
**Action:** Execute clearCart mutation:
```graphql
mutation {
  clearCart {
    id
    items {
      product {
        id
      }
      quantity
    }
    totalPrice
  }
}
```

**Expected Result:**
- All items removed from cart
- Cart is empty
- Total price is zero

**Validation:**
- `cart.items.length` = 0
- `cart.totalPrice` = 0
- `cart.id` remains the same

### Step 11: Add Product with Default Quantity
**Action:** Execute addToCart without specifying quantity (should default to 1):
```graphql
mutation {
  addToCart(input: {
    productId: "product-006"
  }) {
    id
    items {
      product {
        id
      }
      quantity
    }
    totalPrice
  }
}
```

**Expected Result:**
- Product added with quantity 1
- Default quantity parameter works

**Validation:**
- `cart.items.length` = 1
- Item with `product.id` = "product-006" has `quantity` = 1

### Step 12: Add Product with Large Quantity
**Action:** Execute addToCart with large quantity:
```graphql
mutation {
  addToCart(input: {
    productId: "product-007"
    quantity: 100
  }) {
    id
    items {
      product {
        id
      }
      quantity
      totalPrice
    }
    totalPrice
  }
}
```

**Expected Result:**
- Product added with large quantity
- Price calculated correctly for large values

**Validation:**
- Item with `product.id` = "product-007" has `quantity` = 100
- `items[].totalPrice` calculated correctly (no overflow)
- `cart.totalPrice` calculated correctly

### Step 13: Add Non-Existent Product
**Action:** Execute addToCart with invalid product ID:
```graphql
mutation {
  addToCart(input: {
    productId: "non-existent-product-999"
    quantity: 1
  }) {
    id
    items {
      product {
        id
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation returns error
- Error message indicates product not found
- Cart remains unchanged

**Validation:**
- Response contains error
- Error message includes "not found" or similar
- HTTP status may be 400 or 200 with errors array
- Cart state is unchanged from previous step

### Step 14: Add Product with Zero Quantity
**Action:** Execute addToCart with quantity 0:
```graphql
mutation {
  addToCart(input: {
    productId: "product-008"
    quantity: 0
  }) {
    id
    items {
      product {
        id
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation returns error or no-op
- Zero quantity is invalid for adding

**Validation:**
- Error returned indicating invalid quantity
- Or operation is no-op (cart unchanged)
- Product "product-008" not added to cart

### Step 15: Add Product with Negative Quantity
**Action:** Execute addToCart with negative quantity:
```graphql
mutation {
  addToCart(input: {
    productId: "product-009"
    quantity: -5
  }) {
    id
    items {
      product {
        id
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation returns error
- Negative quantity is rejected

**Validation:**
- Response contains error
- Error message indicates invalid quantity
- Cart state is unchanged

### Step 16: Update Non-Existent Cart Item
**Action:** Execute updateCartItem for product not in cart:
```graphql
mutation {
  updateCartItem(input: {
    productId: "product-not-in-cart"
    quantity: 5
  }) {
    id
    items {
      product {
        id
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation returns error or adds item
- Behavior depends on business logic

**Validation:**
- Either error returned with "item not in cart" message
- Or item is added to cart (update becomes add)
- Behavior is consistent with documented API

### Step 17: Remove Non-Existent Cart Item
**Action:** Execute removeFromCart for product not in cart:
```graphql
mutation {
  removeFromCart(productId: "product-not-in-cart") {
    id
    items {
      product {
        id
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation succeeds (no-op) or returns error
- Cart state unchanged

**Validation:**
- Response is successful or contains error
- Cart state unchanged
- No system errors

### Step 18: Verify Cart Persistence Across Queries
**Action:** Execute cart query multiple times:
```graphql
query {
  cart {
    id
    items {
      product {
        id
      }
      quantity
    }
    totalPrice
  }
}
```

**Expected Result:**
- Cart ID remains consistent
- Cart contents persist across queries

**Validation:**
- `cart.id` is same across all queries
- Items remain in cart
- Quantities unchanged
- Total price consistent

### Step 19: Verify Price Calculation Accuracy
**Action:** Add multiple products and verify total calculation:
1. Clear cart
2. Add product A (price: 1000, quantity: 3)
3. Add product B (price: 2500, quantity: 2)
4. Add product C (price: 500, quantity: 10)

```graphql
query {
  cart {
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
- Individual item totals are correct
- Cart total is sum of all items

**Validation:**
- Item A: `totalPrice` = 1000 × 3 = 3000
- Item B: `totalPrice` = 2500 × 2 = 5000
- Item C: `totalPrice` = 500 × 10 = 5000
- `cart.totalPrice` = 3000 + 5000 + 5000 = 13000

### Step 20: Add OFF_SHELF Product to Cart
**Action:** Execute addToCart with OFF_SHELF product:
```graphql
mutation {
  addToCart(input: {
    productId: "off-shelf-product-id"
    quantity: 1
  }) {
    id
    items {
      product {
        id
        state
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation returns error
- OFF_SHELF products cannot be added to cart

**Validation:**
- Response contains error
- Error message indicates product not available
- Cart unchanged

### Step 21: Add Out-of-Stock Product to Cart
**Action:** Execute addToCart with product where countInStock = 0:
```graphql
mutation {
  addToCart(input: {
    productId: "out-of-stock-product-id"
    quantity: 1
  }) {
    id
    items {
      product {
        id
        countInStock
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation returns error
- Out-of-stock products cannot be added

**Validation:**
- Response contains error
- Error message indicates insufficient stock
- Cart unchanged

### Step 22: Add Quantity Exceeding Stock
**Action:** Execute addToCart with quantity > countInStock:
```graphql
mutation {
  addToCart(input: {
    productId: "limited-stock-product-id"
    quantity: 1000
  }) {
    id
    items {
      product {
        id
        countInStock
      }
      quantity
    }
  }
}
```

**Expected Result:**
- Mutation returns error
- Quantity exceeds available stock

**Validation:**
- Response contains error
- Error message indicates insufficient stock
- Shows available stock count
- Cart unchanged

## Success Criteria
- ✅ Cart is auto-created on first query with unique ID
- ✅ Cart ID persists across all operations in session
- ✅ Add to cart works with various quantities
- ✅ Adding same product increments quantity (no duplicates)
- ✅ Update cart item sets quantity to exact value
- ✅ Setting quantity to zero removes item
- ✅ Remove from cart deletes item completely
- ✅ Clear cart empties all items
- ✅ Price calculations are accurate (item and cart totals)
- ✅ Invalid operations return appropriate errors
- ✅ Non-existent products cannot be added
- ✅ OFF_SHELF and out-of-stock products rejected
- ✅ Negative and zero quantities rejected for addToCart
- ✅ Quantity exceeding stock is rejected
- ✅ Cart state is consistent across queries
- ✅ No integer overflow in price calculations

## Notes
- Cart ID should be stored in session/cookie for persistence
- Cart operations are session-specific
- Prices are in cents (integer) to avoid floating-point precision issues
- Business logic should validate stock availability before adding to cart
- Cart total may include discounts or promotions (though not in current scope)
- Cart should clear after successful order placement (tested in place order flow)
