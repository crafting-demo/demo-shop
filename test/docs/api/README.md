# API Test Cases

This directory contains comprehensive API test case documentation for the Demo Shop application. The test cases are organized by API layer and service, covering both GraphQL (customer and admin) and gRPC (backend services) APIs.

## Directory Structure

```
test/docs/api/
├── README.md                                    # This file
├── API-TC001-customer-query-products.md         # Customer products listing
├── API-TC002-customer-query-single-product.md   # Customer product details
├── API-TC003-customer-cart-operations.md        # Customer cart management
├── API-TC004-customer-place-order.md            # Customer order placement
├── API-TC005-admin-query-products-with-filters.md # Admin inventory listing
├── API-TC006-admin-product-crud-operations.md   # Admin product management
├── API-TC007-admin-order-management-operations.md # Admin order management
├── API-TC008-grpc-inventory-service.md          # gRPC Inventory API
├── API-TC009-grpc-cart-service.md               # gRPC Cart API
└── API-TC010-grpc-order-service.md              # gRPC Order API
```

## Test Case Overview

### GraphQL Customer API Tests

#### API-TC001: Customer Query Products
**File:** [API-TC001-customer-query-products.md](API-TC001-customer-query-products.md)  
**Focus:** Customer product listing with pagination  
**Coverage:**
- Query available products with pagination
- Cursor-based navigation
- Product data completeness and validation
- Filtering (only AVAILABLE products with stock)
- OFF_SHELF and out-of-stock products exclusion
- Edge cases (invalid page sizes, last page)

#### API-TC002: Customer Query Single Product
**File:** [API-TC002-customer-query-single-product.md](API-TC002-customer-query-single-product.md)  
**Focus:** Individual product detail retrieval  
**Coverage:**
- Get product by ID (all states, not just AVAILABLE)
- Field data validation (name, price, stock, images, timestamps)
- Non-existent product handling
- Invalid ID handling
- Price and image data format validation
- Special characters and security

#### API-TC003: Customer Cart Operations
**File:** [API-TC003-customer-cart-operations.md](API-TC003-customer-cart-operations.md)  
**Focus:** Shopping cart management  
**Coverage:**
- Cart auto-creation on first query
- Add products (single, multiple, same product)
- Update item quantities
- Remove items (explicit remove and set quantity to 0)
- Clear entire cart
- Price calculations and validation
- Stock availability validation
- Invalid operations (negative quantities, non-existent products, OFF_SHELF products)

#### API-TC004: Customer Place Order
**File:** [API-TC004-customer-place-order.md](API-TC004-customer-place-order.md)  
**Focus:** Order placement from cart  
**Coverage:**
- Create order with valid customer information
- Required field validation (name, email, address)
- Email format validation
- Cart clearing after order
- Order state initialization (PROCESSING)
- Product snapshot preservation
- Invalid operations (empty cart, invalid data)
- Special characters and Unicode handling
- XSS prevention

### GraphQL Admin API Tests

#### API-TC005: Admin Query Products with Filters
**File:** [API-TC005-admin-query-products-with-filters.md](API-TC005-admin-query-products-with-filters.md)  
**Focus:** Admin inventory listing with filters  
**Coverage:**
- Query all products (including OFF_SHELF)
- Filter by state (AVAILABLE, OFF_SHELF)
- Search by name (case-insensitive, partial match)
- Combined filters (state + search)
- Pagination with filters
- Out-of-stock products included (unlike customer API)
- Large page sizes and performance

#### API-TC006: Admin Product CRUD Operations
**File:** [API-TC006-admin-product-crud-operations.md](API-TC006-admin-product-crud-operations.md)  
**Focus:** Product creation, update, and deletion  
**Coverage:**
- Create products (complete data, minimal data, various states)
- Update products (single field, multiple fields)
- Update state (on/off shelf toggle)
- Delete products (soft delete)
- Field validation (required fields, valid ranges)
- Timestamp management (created_at, updated_at)
- Special characters, Unicode, and security
- Image data handling

#### API-TC007: Admin Order Management Operations
**File:** [API-TC007-admin-order-management-operations.md](API-TC007-admin-order-management-operations.md)  
**Focus:** Order lifecycle management  
**Coverage:**
- Query orders with pagination
- Filter by state (PROCESSING, SHIPPED, COMPLETED, CANCELED)
- Filter by customer email
- Update order states (ship, complete, cancel)
- Valid state transitions enforcement
- Invalid state transitions rejection
- Terminal states (COMPLETED, CANCELED)
- Order data immutability
- Timestamp updates

### gRPC Backend API Tests

#### API-TC008: gRPC InventoryService
**File:** [API-TC008-grpc-inventory-service.md](API-TC008-grpc-inventory-service.md)  
**Focus:** Backend inventory management service  
**Coverage:**
- QueryProducts (pagination, filtering by state)
- GetProduct (by ID)
- CreateProduct (with validation)
- UpdateProduct (partial updates with wrapped types)
- DeleteProduct (soft delete)
- Protobuf message validation
- Timestamp format (google.protobuf.Timestamp)
- State enum values
- Error codes (NOT_FOUND, INVALID_ARGUMENT)

#### API-TC009: gRPC CartService
**File:** [API-TC009-grpc-cart-service.md](API-TC009-grpc-cart-service.md)  
**Focus:** Backend cart management service  
**Coverage:**
- GetCart (auto-creation)
- AddProductToCart (increment quantities)
- UpdateProductInCart (set absolute quantity)
- ClearCart
- Product snapshot handling
- Stock availability validation
- Multiple cart isolation
- Protobuf message structures
- Error codes (NOT_FOUND, INVALID_ARGUMENT, FAILED_PRECONDITION)

#### API-TC010: gRPC OrderService
**File:** [API-TC010-grpc-order-service.md](API-TC010-grpc-order-service.md)  
**Focus:** Backend order management service  
**Coverage:**
- CreateOrder (from cart)
- QueryOrders (pagination, state filtering)
- GetOrder (by ID)
- UpdateOrder (state transitions)
- State machine enforcement
- Valid transitions (PROCESSING→SHIPPED→COMPLETED, cancellation)
- Invalid transitions rejection
- Order data immutability
- Product snapshot preservation
- Total calculation validation

## Test Execution Guidelines

### Prerequisites

**Services Required:**
- Frontend service (frontd) running on port 8080
- Transaction service (transd) running on port 9090
- PostgreSQL database accessible and migrated

**Setup Commands:**
```bash
# Build all services
./scripts/build-all.sh

# Run database migrations
./scripts/db-migrate.sh

# Start frontend service
./bin/frontd &

# Start transaction service
./bin/transd &
```

**Test Tools:**
- GraphQL: curl, Postman, Insomnia, or Apollo Studio
- gRPC: grpcurl, BloomRPC, or Postman

### Test Data Requirements

**Products:**
- Minimum 50-100 products for pagination tests
- Mix of states: 70% AVAILABLE, 30% OFF_SHELF
- Various price ranges: 500-500000 cents (smallest currency unit)
- Stock counts: 0-1000
- Products with and without descriptions/images
- Products with special characters and Unicode in names

**Orders:**
- Minimum 30 orders across all states:
  - 30% PROCESSING
  - 25% SHIPPED
  - 35% COMPLETED
  - 10% CANCELED
- Various customer emails (for filtering tests)
- Range of dates and total prices

**Carts:**
- Test carts with 1-10 items
- Various quantities per item
- Mixed product types

### Execution Order

#### Phase 1: Backend gRPC Services (Foundation)
1. API-TC008: gRPC InventoryService
2. API-TC009: gRPC CartService
3. API-TC010: gRPC OrderService

#### Phase 2: Customer GraphQL API (Customer Flow)
4. API-TC001: Customer Query Products
5. API-TC002: Customer Query Single Product
6. API-TC003: Customer Cart Operations
7. API-TC004: Customer Place Order

#### Phase 3: Admin GraphQL API (Admin Flow)
8. API-TC005: Admin Query Products with Filters
9. API-TC006: Admin Product CRUD Operations
10. API-TC007: Admin Order Management Operations

### GraphQL Testing

**Customer Endpoint:** `http://localhost:8080/graphql`  
**Admin Endpoint:** `http://localhost:8080/admin/graphql`

**Example curl command:**
```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { products(first: 10) { edges { node { id name pricePerUnit } } } }"}'
```

### gRPC Testing

**Service Endpoint:** `localhost:9090`

**Example grpcurl commands:**
```bash
# List available services
grpcurl -plaintext localhost:9090 list

# List methods in a service
grpcurl -plaintext localhost:9090 list demoshop.v1.InventoryService

# Call a method
grpcurl -plaintext -d '{"pagination": {"first": 10}}' \
  localhost:9090 demoshop.v1.InventoryService/QueryProducts
```

## Test Coverage Summary

### Functional Coverage
- ✅ Product browsing and search (customer and admin)
- ✅ Shopping cart management (add, update, remove, clear)
- ✅ Order placement and checkout
- ✅ Admin inventory management (CRUD operations)
- ✅ Admin order lifecycle management
- ✅ GraphQL queries and mutations (customer and admin)
- ✅ gRPC service methods (all three services)

### Data Validation Coverage
- ✅ Required field validation
- ✅ Data type validation
- ✅ Value range validation (price > 0, quantity ≥ 0)
- ✅ Email format validation
- ✅ State enum validation
- ✅ Timestamp format validation
- ✅ Image data format validation (data URI scheme)

### Business Logic Coverage
- ✅ Product availability filtering (AVAILABLE only for customers)
- ✅ Stock availability validation
- ✅ Cart quantity management (add increments, update sets)
- ✅ Order state machine (valid and invalid transitions)
- ✅ Product snapshots in orders (immutability)
- ✅ Price calculations (no floating-point errors)
- ✅ Cart clearing after order placement

### Error Handling Coverage
- ✅ Invalid IDs (non-existent entities)
- ✅ Missing required fields
- ✅ Invalid field values (negative prices, zero quantities)
- ✅ Invalid state transitions
- ✅ Empty carts
- ✅ Insufficient stock
- ✅ OFF_SHELF products in cart
- ✅ Special characters and XSS attempts

### Non-Functional Coverage
- ✅ Pagination (cursor-based)
- ✅ Filtering and search
- ✅ Performance (large page sizes)
- ✅ Concurrency (basic)
- ✅ Security (XSS prevention, SQL injection prevention)
- ✅ Unicode and internationalization
- ✅ Data integrity and consistency

## API Coverage Matrix

| API Layer | Service/Area | Methods/Operations | Test Case |
|-----------|--------------|-------------------|-----------|
| GraphQL Customer | Products | products, product | API-TC001, API-TC002 |
| GraphQL Customer | Cart | cart, addToCart, updateCartItem, removeFromCart, clearCart | API-TC003 |
| GraphQL Customer | Orders | placeOrder | API-TC004 |
| GraphQL Admin | Products | products (with filters), product | API-TC005 |
| GraphQL Admin | Products | createProduct, updateProduct, putProductOnShelf, takeProductOffShelf, removeProduct | API-TC006 |
| GraphQL Admin | Orders | orders, order, shipOrder, completeOrder, cancelOrder | API-TC007 |
| gRPC | InventoryService | QueryProducts, GetProduct, CreateProduct, UpdateProduct, DeleteProduct | API-TC008 |
| gRPC | CartService | GetCart, AddProductToCart, UpdateProductInCart, ClearCart | API-TC009 |
| gRPC | OrderService | CreateOrder, QueryOrders, GetOrder, UpdateOrder | API-TC010 |

## Validation Standards

### Response Validation
All test cases validate:
- HTTP/gRPC status codes
- Response structure and schema
- Data accuracy (values match expected)
- Timestamp formats (ISO 8601 for GraphQL, google.protobuf.Timestamp for gRPC)
- Error messages and codes
- Field presence and types

### Data Integrity Validation
- Price calculations accurate (no rounding errors)
- Quantity tracking accurate
- State transitions valid only
- Immutability (IDs, created_at timestamps, product snapshots in orders)
- Referential integrity (products exist when referenced)

### Error Code Standards

**GraphQL:**
- HTTP 200 with errors array for business logic errors
- HTTP 400 for validation errors
- HTTP 404 for not found (if applicable)
- HTTP 500 for server errors

**gRPC:**
- OK (0): Success
- INVALID_ARGUMENT (3): Invalid parameters
- NOT_FOUND (5): Entity not found
- FAILED_PRECONDITION (9): Business logic violation (e.g., invalid state transition)
- INTERNAL (13): Server errors

## Success Criteria

A test case passes when:
1. ✅ All test steps execute without errors
2. ✅ All validation checks pass
3. ✅ Expected results match actual results
4. ✅ No data corruption or inconsistencies
5. ✅ Error cases return appropriate error codes
6. ✅ Performance within acceptable limits
7. ✅ Security checks pass (no XSS, injection vulnerabilities)

## Bug Reporting

When a test fails, document:
1. **Test Case ID** and step number
2. **Expected Result** vs **Actual Result**
3. **Error Messages** and stack traces
4. **Request/Response Payloads** (sanitize sensitive data)
5. **Environment Details** (service versions, database state)
6. **Steps to Reproduce**
7. **Screenshots** (for GraphQL IDE tools)

## Maintenance

### Updating Test Cases
When requirements or APIs change:
1. Review affected test cases
2. Update test steps and validation criteria
3. Update expected results
4. Verify test data requirements
5. Re-execute affected tests
6. Document changes in test case history

### Adding New Test Cases
Follow the existing format:
- **Summary**: Brief description of what is being tested
- **Description**: Detailed explanation of test scope
- **Prerequisites**: Services, data, and tools needed
- **Test Steps**: Numbered steps with actions, expected results, and validations
- **Success Criteria**: Overall pass conditions
- **Notes**: Additional context, business logic, or technical details

## Key Concepts

### Cursor-Based Pagination
All list queries use cursor-based pagination:
- `first`: Number of items to fetch
- `after`: Cursor to start from
- `pageInfo`: Contains `hasNextPage`, `hasPreviousPage`, `startCursor`, `endCursor`, `totalCount`

### Product States
- **AVAILABLE** (1): Product is on shelf and available for purchase
- **OFF_SHELF** (2): Product is hidden from customers

### Order State Machine
Valid transitions:
- PROCESSING → SHIPPED → COMPLETED (happy path)
- PROCESSING → CANCELED (cancel before shipping)
- SHIPPED → CANCELED (cancel after shipping)

Terminal states:
- COMPLETED (cannot change)
- CANCELED (cannot change)

### Price Handling
- Prices stored as integers in **smallest currency unit** (e.g., cents)
- Avoids floating-point precision issues
- Example: $19.99 = 1999 cents

### Image Data Format
- Uses **data URI scheme**: `data:image/{type};base64,{base64_data}`
- Example: `data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...`

### Product Snapshots
- Orders contain **immutable product snapshots** at time of purchase
- Price changes in inventory don't affect existing orders
- Preserves historical accuracy

## Tools and Resources

### Recommended Testing Tools

**GraphQL:**
- [Postman](https://www.postman.com/) - API testing platform
- [Insomnia](https://insomnia.rest/) - API client
- [Apollo Studio](https://studio.apollographql.com/) - GraphQL IDE

**gRPC:**
- [grpcurl](https://github.com/fullstorydev/grpcurl) - Command-line tool
- [BloomRPC](https://github.com/bloomrpc/bloomrpc) - GUI client
- [Postman](https://www.postman.com/) - Also supports gRPC

**Automation:**
- [Playwright](https://playwright.dev/) - E2E testing
- [Jest](https://jestjs.io/) - JavaScript testing framework
- [Go testing](https://golang.org/pkg/testing/) - Go native testing

### Documentation References
- [App Requirements](../../docs/App.md)
- [Frontend Service](../../docs/FrondendService.md)
- [Transaction Service](../../docs/TransactionService.md)
- [GraphQL Schema](../../src/apis/graphql/)
- [gRPC Proto Definitions](../../src/apis/proto/)

## Contact and Support

For questions or issues:
- Review the [AGENTS.md](../../AGENTS.md) guide
- Check existing flow tests in [test/docs/flows/](../flows/)
- Refer to API definitions in [src/apis/](../../src/apis/)

---

**Last Updated:** 2026-01-14  
**Total API Test Cases:** 10  
**Coverage:** Comprehensive (Customer API, Admin API, Backend gRPC Services)  
**Status:** ✅ Complete
