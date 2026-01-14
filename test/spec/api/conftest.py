"""Pytest configuration and fixtures."""
import pytest
from typing import Generator

from config import config
from utils.graphql_client import CustomerGraphQLClient, AdminGraphQLClient
from utils.grpc_client import InventoryServiceClient, CartServiceClient, OrderServiceClient


@pytest.fixture(scope="session")
def customer_graphql_client() -> Generator[CustomerGraphQLClient, None, None]:
    """Provide customer GraphQL client."""
    client = CustomerGraphQLClient(config.customer_graphql_url, timeout=config.test_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def admin_graphql_client() -> Generator[AdminGraphQLClient, None, None]:
    """Provide admin GraphQL client."""
    client = AdminGraphQLClient(config.admin_graphql_url, timeout=config.test_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def inventory_service_client() -> Generator[InventoryServiceClient, None, None]:
    """Provide gRPC InventoryService client."""
    client = InventoryServiceClient(config.grpc_host, config.grpc_port)
    yield client
    client.close()


@pytest.fixture(scope="session")
def cart_service_client() -> Generator[CartServiceClient, None, None]:
    """Provide gRPC CartService client."""
    client = CartServiceClient(config.grpc_host, config.grpc_port)
    yield client
    client.close()


@pytest.fixture(scope="session")
def order_service_client() -> Generator[OrderServiceClient, None, None]:
    """Provide gRPC OrderService client."""
    client = OrderServiceClient(config.grpc_host, config.grpc_port)
    yield client
    client.close()


@pytest.fixture(scope="function")
def unique_cart_id() -> str:
    """Generate unique cart ID for test isolation."""
    import uuid
    return f"test-cart-{uuid.uuid4()}"


@pytest.fixture(scope="function")
def test_product_ids(customer_graphql_client: CustomerGraphQLClient) -> list[str]:
    """Provide list of test product IDs.
    
    Queries available products dynamically.
    """
    result = customer_graphql_client.query_products(first=10)
    edges = result['data']['products']['edges']
    
    if len(edges) < 3:
        pytest.skip("Not enough test products available")
    
    return [edge['node']['id'] for edge in edges[:5]]


@pytest.fixture(scope="function")
def test_product_id(test_product_ids: list) -> str:
    """Provide single test product ID."""
    return test_product_ids[0]


@pytest.fixture(scope="function")
def available_product_id(customer_graphql_client: CustomerGraphQLClient) -> str:
    """Provide an AVAILABLE product ID."""
    result = customer_graphql_client.query_products(first=1)
    edges = result['data']['products']['edges']
    
    if not edges:
        pytest.skip("No AVAILABLE products in database")
    
    return edges[0]['node']['id']


@pytest.fixture(scope="function")
def off_shelf_product_id(admin_graphql_client: AdminGraphQLClient) -> str:
    """Provide an OFF_SHELF product ID."""
    result = admin_graphql_client.query_products(first=50, state_filter='OFF_SHELF')
    edges = result['data']['products']['edges']
    
    if not edges:
        pytest.skip("No OFF_SHELF products in database")
    
    return edges[0]['node']['id']


@pytest.fixture(scope="function")
def out_of_stock_product_id(admin_graphql_client: AdminGraphQLClient) -> str:
    """Provide a product ID with zero stock."""
    result = admin_graphql_client.query_products(first=100)
    edges = result['data']['products']['edges']
    
    for edge in edges:
        if edge['node']['countInStock'] == 0:
            return edge['node']['id']
    
    pytest.skip("No out-of-stock products in database")


@pytest.fixture(scope="function")
def product_with_image_id(admin_graphql_client: AdminGraphQLClient) -> str:
    """Provide a product ID that has image data."""
    result = admin_graphql_client.query_products(first=100)
    edges = result['data']['products']['edges']
    
    for edge in edges:
        if edge['node'].get('imageData'):
            return edge['node']['id']
    
    # If no product with image, create one
    from utils.helpers import generate_test_image_data
    product_result = admin_graphql_client.create_product(
        name="Test Product with Image",
        price_per_unit=1000,
        count_in_stock=5,
        image_data=generate_test_image_data()
    )
    return product_result['data']['createProduct']['id']


@pytest.fixture(scope="function")
def test_order_email(admin_graphql_client: AdminGraphQLClient) -> str:
    """Provide a customer email that has orders."""
    result = admin_graphql_client.query_orders(first=1)
    edges = result['data']['orders']['edges']
    
    if not edges:
        pytest.skip("No orders in database")
    
    return edges[0]['node']['customerEmail']


# Rename alias fixtures for better compatibility
@pytest.fixture(scope="session")
def inventory_grpc_client(inventory_service_client: InventoryServiceClient) -> InventoryServiceClient:
    """Alias for inventory_service_client."""
    return inventory_service_client


@pytest.fixture(scope="session")
def cart_grpc_client(cart_service_client: CartServiceClient) -> CartServiceClient:
    """Alias for cart_service_client."""
    return cart_service_client


@pytest.fixture(scope="session")
def order_grpc_client(order_service_client: OrderServiceClient) -> OrderServiceClient:
    """Alias for order_service_client."""
    return order_service_client


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "customer: Customer-facing API tests")
    config.addinivalue_line("markers", "admin: Admin-facing API tests")
    config.addinivalue_line("markers", "grpc: gRPC backend service tests")
    config.addinivalue_line("markers", "graphql: GraphQL API tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "integration: Integration tests requiring all services")
