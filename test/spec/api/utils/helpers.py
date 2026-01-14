"""Helper functions for tests."""
import time
import socket
import base64
from typing import Optional


def wait_for_service(host: str, port: int, timeout: int = 30) -> bool:
    """Wait for a service to be available.
    
    Args:
        host: Service host
        port: Service port
        timeout: Timeout in seconds
        
    Returns:
        True if service is available, False otherwise
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except socket.error:
            pass
        time.sleep(0.5)
    return False


def generate_test_image_data(width: int = 1, height: int = 1, format: str = "png") -> str:
    """Generate test image data in data URI format.
    
    Creates a minimal valid image for testing purposes.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (png, jpeg, gif)
        
    Returns:
        Image data URI string
    """
    # Minimal 1x1 PNG (base64 encoded)
    if format == "png":
        # This is a valid 1x1 transparent PNG
        image_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        mime_type = "image/png"
    elif format == "jpeg" or format == "jpg":
        # Minimal 1x1 JPEG
        image_bytes = base64.b64decode(
            "/9j/4AAQSkZJRgABAQEAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/AB//2Q=="
        )
        mime_type = "image/jpeg"
    elif format == "gif":
        # Minimal 1x1 GIF
        image_bytes = base64.b64decode(
            "R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
        )
        mime_type = "image/gif"
    else:
        raise ValueError(f"Unsupported image format: {format}")
    
    # Encode to base64 and create data URI
    b64_data = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64_data}"


def validate_iso8601_timestamp(timestamp_str: str) -> bool:
    """Validate ISO 8601 timestamp format.
    
    Args:
        timestamp_str: Timestamp string to validate
        
    Returns:
        True if valid ISO 8601 format
    """
    try:
        from datetime import datetime
        # Try parsing with timezone
        try:
            datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return True
        except:
            # Try parsing without timezone
            datetime.fromisoformat(timestamp_str)
            return True
    except:
        return False


def validate_price(price: int) -> bool:
    """Validate price value.
    
    Args:
        price: Price in cents
        
    Returns:
        True if valid price
    """
    return isinstance(price, int) and price > 0


def validate_quantity(quantity: int, allow_zero: bool = False) -> bool:
    """Validate quantity value.
    
    Args:
        quantity: Quantity value
        allow_zero: Whether zero is allowed
        
    Returns:
        True if valid quantity
    """
    if not isinstance(quantity, int):
        return False
    if allow_zero:
        return quantity >= 0
    return quantity > 0


def validate_data_uri(data_uri: str, expected_mime_type: Optional[str] = None) -> bool:
    """Validate data URI format.
    
    Args:
        data_uri: Data URI string
        expected_mime_type: Expected MIME type (e.g., 'image/png')
        
    Returns:
        True if valid data URI
    """
    if not data_uri.startswith("data:"):
        return False
    
    try:
        parts = data_uri.split(";", 1)
        mime_type = parts[0][5:]  # Remove "data:" prefix
        
        if expected_mime_type and mime_type != expected_mime_type:
            return False
        
        if len(parts) > 1:
            encoding_and_data = parts[1].split(",", 1)
            if len(encoding_and_data) != 2:
                return False
            encoding = encoding_and_data[0]
            data = encoding_and_data[1]
            
            if encoding == "base64":
                # Validate base64
                try:
                    base64.b64decode(data)
                    return True
                except:
                    return False
        
        return False
    except:
        return False


def validate_grpc_timestamp(timestamp) -> bool:
    """Validate gRPC timestamp (google.protobuf.Timestamp).
    
    Args:
        timestamp: Protobuf Timestamp object
        
    Returns:
        True if valid timestamp
    """
    try:
        # Check if it has required attributes
        return hasattr(timestamp, 'seconds') and hasattr(timestamp, 'nanos')
    except:
        return False


def calculate_cart_total(items: list) -> int:
    """Calculate cart total price from items.
    
    Args:
        items: List of cart items with quantity and product.pricePerUnit
        
    Returns:
        Total price in cents
    """
    total = 0
    for item in items:
        total += item['quantity'] * item['product']['pricePerUnit']
    return total


def calculate_order_total(items: list) -> int:
    """Calculate order total price from items.
    
    Args:
        items: List of order items with quantity and totalPrice
        
    Returns:
        Total price in cents
    """
    total = 0
    for item in items:
        total += item['totalPrice']
    return total
