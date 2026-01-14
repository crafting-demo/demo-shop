#!/usr/bin/env python3
"""Validate test suite structure without running tests."""

import os
import sys
from pathlib import Path

def check_file_structure():
    """Check that all expected files exist."""
    base_dir = Path(__file__).parent
    
    required_files = [
        "config.py",
        "conftest.py",
        "pyproject.toml",
        ".env",
        "utils/__init__.py",
        "utils/graphql_client.py",
        "utils/grpc_client.py",
        "utils/helpers.py",
        "tests/__init__.py",
        "tests/graphql/__init__.py",
        "tests/graphql/customer/__init__.py",
        "tests/graphql/admin/__init__.py",
        "tests/grpc/__init__.py",
    ]
    
    test_files = [
        # Customer GraphQL tests
        "tests/graphql/customer/test_query_products.py",
        "tests/graphql/customer/test_query_single_product.py",
        "tests/graphql/customer/test_cart_operations.py",
        "tests/graphql/customer/test_place_order.py",
        # Admin GraphQL tests
        "tests/graphql/admin/test_product_crud.py",
        "tests/graphql/admin/test_query_products_filters.py",
        "tests/graphql/admin/test_order_management.py",
        # gRPC tests
        "tests/grpc/test_inventory_service.py",
        "tests/grpc/test_cart_service.py",
        "tests/grpc/test_order_service.py",
    ]
    
    print("=== Test Suite Structure Validation ===\n")
    
    print("Checking required files...")
    all_good = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_good = False
    
    print("\nChecking test files...")
    for file_path in test_files:
        full_path = base_dir / file_path
        if full_path.exists():
            # Count test methods
            with open(full_path, 'r') as f:
                content = f.read()
                test_count = content.count('def test_')
            print(f"  ✓ {file_path} ({test_count} tests)")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_good = False
    
    return all_good

def check_imports():
    """Check if critical imports work."""
    print("\nChecking Python imports...")
    
    imports_to_check = [
        ("config", "Configuration"),
        ("utils.graphql_client", "GraphQL clients"),
        ("utils.grpc_client", "gRPC clients"),
        ("utils.helpers", "Helper functions"),
    ]
    
    all_good = True
    for module_name, description in imports_to_check:
        try:
            __import__(module_name)
            print(f"  ✓ {description} ({module_name})")
        except ImportError as e:
            print(f"  ✗ {description} ({module_name}) - {e}")
            all_good = False
    
    return all_good

def count_test_methods():
    """Count total test methods."""
    base_dir = Path(__file__).parent
    test_dir = base_dir / "tests"
    
    total_tests = 0
    test_files = []
    
    for test_file in test_dir.rglob("test_*.py"):
        with open(test_file, 'r') as f:
            content = f.read()
            count = content.count('def test_')
            total_tests += count
            test_files.append((test_file.relative_to(base_dir), count))
    
    print(f"\nTest files found: {len(test_files)}")
    print(f"Total test methods: {total_tests}")
    
    return total_tests

def main():
    """Main validation."""
    os.chdir(Path(__file__).parent)
    
    structure_ok = check_file_structure()
    imports_ok = check_imports()
    total_tests = count_test_methods()
    
    print("\n=== Validation Summary ===")
    print(f"  File structure: {'✓ PASS' if structure_ok else '✗ FAIL'}")
    print(f"  Python imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"  Total tests: {total_tests}")
    
    if structure_ok and imports_ok and total_tests > 0:
        print("\n✓ Test suite structure is valid!")
        print("\nTo run tests (once dependencies are installed):")
        print("  python3 -m pytest")
        print("  python3 -m pytest -m graphql")
        print("  python3 -m pytest tests/graphql/customer/test_query_products.py")
        return 0
    else:
        print("\n✗ Test suite has issues. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
