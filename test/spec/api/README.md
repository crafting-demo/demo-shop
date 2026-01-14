# API Test Suite

Automated test suite for Demo Shop APIs, including GraphQL (customer and admin) and gRPC (backend services) tests.

## Overview

This test suite implements all test cases documented in `test/docs/api/` with executable test code using Python and pytest.

## Structure

```
test/spec/api/
├── pyproject.toml           # Project configuration and dependencies
├── .python-version          # Python version
├── README.md                # This file
├── pytest.ini               # Pytest configuration
├── conftest.py              # Pytest fixtures and configuration
├── config.py                # Test configuration
├── requirements.txt         # Generated from pyproject.toml
├── utils/                   # Test utilities
│   ├── __init__.py
│   ├── graphql_client.py    # GraphQL client wrapper
│   ├── grpc_client.py       # gRPC client wrapper
│   ├── helpers.py           # Helper functions
│   └── fixtures.py          # Test data fixtures
├── tests/                   # Test cases
│   ├── __init__.py
│   ├── graphql/             # GraphQL tests
│   │   ├── __init__.py
│   │   ├── customer/        # Customer API tests
│   │   │   ├── __init__.py
│   │   │   ├── test_query_products.py      # API-TC001
│   │   │   ├── test_query_product.py       # API-TC002
│   │   │   ├── test_cart_operations.py     # API-TC003
│   │   │   └── test_place_order.py         # API-TC004
│   │   └── admin/           # Admin API tests
│   │       ├── __init__.py
│   │       ├── test_query_products.py      # API-TC005
│   │       ├── test_product_crud.py        # API-TC006
│   │       └── test_order_management.py    # API-TC007
│   └── grpc/                # gRPC tests
│       ├── __init__.py
│       ├── test_inventory_service.py       # API-TC008
│       ├── test_cart_service.py            # API-TC009
│       └── test_order_service.py           # API-TC010
└── proto/                   # Generated gRPC stubs
    └── demoshop/
        └── v1/
```

## Setup

### Prerequisites

- Python 3.13+
- Demo Shop services running:
  - Frontend service (frontd) on port 8080
  - Transaction service (transd) on port 9090
- Database populated with test data

### Installation

```bash
cd test/spec/api

# Install uv (Python package manager) if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Generate gRPC stubs from proto files
./gen-proto.sh
```

**Note:** The `gen-proto.sh` script automatically fixes imports in the generated protobuf files to use the `proto.` prefix. This ensures that imports work correctly from the test files.

If you need to regenerate the proto files manually:
```bash
# Generate proto files
./gen-proto.sh

# Or fix imports in existing generated files
python3 fix_proto_imports.py
```

### Configuration

Create a `.env` file in this directory:

```env
# Service endpoints
FRONTEND_URL=http://localhost:8080
GRPC_HOST=localhost
GRPC_PORT=9090

# GraphQL endpoints
CUSTOMER_GRAPHQL_URL=http://localhost:8080/graphql
ADMIN_GRAPHQL_URL=http://localhost:8081/graphql

# Test configuration
TEST_TIMEOUT=30
ENABLE_SLOW_TESTS=false
```

## Running Tests

### Run all tests

```bash
uv run pytest
```

### Run specific test categories
```bash
# GraphQL tests only
uv run pytest -m graphql

# gRPC tests only
uv run pytest -m grpc

# Customer API tests
uv run pytest -m customer

# Admin API tests
uv run pytest -m admin
```

### Run specific test files
```bash
# Customer product query tests
uv run pytest tests/graphql/customer/test_query_products.py

# gRPC inventory service tests
uv run pytest tests/grpc/test_inventory_service.py
```

### Run in parallel
```bash
uv run pytest -n auto
```

### Run with verbose output
```bash
uv run pytest -v -s
```

## Test Case Mapping

| Test File | Test Case Doc | Description |
|-----------|---------------|-------------|
| `tests/graphql/customer/test_query_products.py` | API-TC001 | Customer query products with pagination |
| `tests/graphql/customer/test_query_product.py` | API-TC002 | Customer query single product |
| `tests/graphql/customer/test_cart_operations.py` | API-TC003 | Customer cart operations |
| `tests/graphql/customer/test_place_order.py` | API-TC004 | Customer place order |
| `tests/graphql/admin/test_query_products.py` | API-TC005 | Admin query products with filters |
| `tests/graphql/admin/test_product_crud.py` | API-TC006 | Admin product CRUD operations |
| `tests/graphql/admin/test_order_management.py` | API-TC007 | Admin order management |
| `tests/grpc/test_inventory_service.py` | API-TC008 | gRPC InventoryService |
| `tests/grpc/test_cart_service.py` | API-TC009 | gRPC CartService |
| `tests/grpc/test_order_service.py` | API-TC010 | gRPC OrderService |
