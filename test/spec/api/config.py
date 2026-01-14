"""Configuration for API tests."""
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Test configuration."""

    # Service endpoints
    frontend_url: str
    grpc_host: str
    grpc_port: int

    # GraphQL endpoints
    customer_graphql_url: str
    admin_graphql_url: str

    # Test configuration
    test_timeout: int
    enable_slow_tests: bool

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:8080"),
            grpc_host=os.getenv("GRPC_HOST", "localhost"),
            grpc_port=int(os.getenv("GRPC_PORT", "9000")),
            customer_graphql_url=os.getenv(
                "CUSTOMER_GRAPHQL_URL", "http://localhost:8080/graphql"
            ),
            admin_graphql_url=os.getenv(
                "ADMIN_GRAPHQL_URL", "http://localhost:8081/graphql"
            ),
            test_timeout=int(os.getenv("TEST_TIMEOUT", "30")),
            enable_slow_tests=os.getenv("ENABLE_SLOW_TESTS", "false").lower() == "true",
        )


# Global config instance
config = Config.from_env()
