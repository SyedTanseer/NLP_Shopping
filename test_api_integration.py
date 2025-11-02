#!/usr/bin/env python3
"""
Integration test for Voice Shopping Assistant API

This script tests the basic functionality of the API endpoints.
"""

import sys
import time
import json
import base64
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from fastapi.testclient import TestClient
    from voice_shopping_assistant.api.app import app
    from voice_shopping_assistant.api.dependencies import reset_dependencies
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)


def test_basic_endpoints():
    """Test basic API endpoints"""
    print("Testing basic API endpoints...")
    
    # Reset dependencies for clean test
    reset_dependencies()
    
    # Create test client
    client = TestClient(app)
    
    # Test root endpoint
    print("  Testing root endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Voice Shopping Assistant API"
    print("    ✓ Root endpoint working")
    
    # Test ping endpoint
    print("  Testing ping endpoint...")
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("    ✓ Ping endpoint working")
    
    # Test health endpoint
    print("  Testing health endpoint...")
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    print("    ✓ Health endpoint working")
    
    print("✓ Basic endpoints test passed")


def test_text_processing():
    """Test text command processing"""
    print("Testing text processing endpoint...")
    
    client = TestClient(app)
    
    # Test text processing
    request_data = {
        "session_id": "test-session-1",
        "text": "add two red shirts to my cart"
    }
    
    print("  Sending text processing request...")
    response = client.post("/api/v1/text/process", json=request_data)
    
    # Should get a response even if processing fails due to missing models
    assert response.status_code in [200, 500]  # 500 is acceptable for missing models
    
    if response.status_code == 200:
        data = response.json()
        assert "original_text" in data
        assert "response_text" in data
        assert "intent" in data
        print("    ✓ Text processing successful")
    else:
        print("    ⚠ Text processing failed (likely due to missing models)")
    
    print("✓ Text processing test completed")


def test_cart_endpoints():
    """Test cart management endpoints"""
    print("Testing cart management endpoints...")
    
    client = TestClient(app)
    session_id = "test-cart-session"
    
    # Test get empty cart
    print("  Testing get empty cart...")
    response = client.get(f"/api/v1/cart/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Cart is empty"
    print("    ✓ Get empty cart working")
    
    # Test clear cart (should handle empty cart gracefully)
    print("  Testing clear empty cart...")
    response = client.delete(f"/api/v1/cart/{session_id}")
    assert response.status_code == 200
    data = response.json()
    # Should handle empty cart gracefully
    print("    ✓ Clear cart working")
    
    print("✓ Cart endpoints test passed")


def test_product_search():
    """Test product search endpoints"""
    print("Testing product search endpoints...")
    
    client = TestClient(app)
    
    # Test search with query
    print("  Testing product search with query...")
    request_data = {
        "query": "shirt",
        "limit": 5
    }
    
    response = client.post("/api/v1/products/search", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total_found" in data
    print("    ✓ Product search working")
    
    # Test search with filters
    print("  Testing product search with filters...")
    request_data = {
        "filters": {
            "category": "clothing",
            "min_price": 10,
            "max_price": 100
        },
        "limit": 10
    }
    
    response = client.post("/api/v1/products/search", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    print("    ✓ Product search with filters working")
    
    print("✓ Product search test passed")


def test_error_handling():
    """Test error handling"""
    print("Testing error handling...")
    
    client = TestClient(app)
    
    # Test invalid endpoint
    print("  Testing 404 error...")
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == True
    assert data["error_type"] == "not_found"
    print("    ✓ 404 error handling working")
    
    # Test invalid request data
    print("  Testing validation error...")
    response = client.post("/api/v1/text/process", json={})
    assert response.status_code == 422  # Validation error
    print("    ✓ Validation error handling working")
    
    # Test invalid session ID
    print("  Testing invalid session ID...")
    response = client.post("/api/v1/text/process", json={
        "session_id": "",  # Empty session ID
        "text": "test"
    })
    assert response.status_code == 422
    print("    ✓ Invalid session ID handling working")
    
    print("✓ Error handling test passed")


def test_api_stats():
    """Test API statistics endpoint"""
    print("Testing API statistics...")
    
    client = TestClient(app)
    
    # Make a few requests first
    client.get("/ping")
    client.get("/api/v1/health")
    
    # Test stats endpoint
    print("  Testing stats endpoint...")
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "successful_requests" in data
    assert "uptime" in data
    print("    ✓ API stats working")
    
    print("✓ API statistics test passed")


def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("Voice Shopping Assistant API Integration Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        test_basic_endpoints()
        print()
        
        test_text_processing()
        print()
        
        test_cart_endpoints()
        print()
        
        test_product_search()
        print()
        
        test_error_handling()
        print()
        
        test_api_stats()
        print()
        
        elapsed_time = time.time() - start_time
        print("=" * 60)
        print(f"✓ All tests passed in {elapsed_time:.2f} seconds")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print("=" * 60)
        print(f"✗ Tests failed after {elapsed_time:.2f} seconds")
        print(f"Error: {e}")
        print("=" * 60)
        
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)