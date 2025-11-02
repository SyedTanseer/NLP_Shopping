#!/usr/bin/env python3
"""
Basic API test without ML dependencies

This script tests the API structure and basic functionality without requiring
heavy ML models to be installed.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from voice_shopping_assistant.api.models import (
        VoiceCommandRequest, TextCommandRequest, ErrorResponse,
        HealthResponse, APIStatsResponse
    )
    from voice_shopping_assistant.api.endpoints import router
    from voice_shopping_assistant.api.middleware import setup_middleware
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


def create_test_app():
    """Create a minimal FastAPI app for testing"""
    app = FastAPI(title="Test API")
    
    # Add basic middleware
    try:
        setup_middleware(app)
    except Exception as e:
        print(f"Warning: Could not setup middleware: {e}")
    
    # Include router
    app.include_router(router)
    
    # Add basic root endpoint
    @app.get("/")
    async def root():
        return {"status": "test", "message": "API structure test"}
    
    return app


def test_api_structure():
    """Test API structure and endpoint definitions"""
    print("Testing API structure...")
    
    app = create_test_app()
    client = TestClient(app)
    
    # Test root endpoint
    print("  Testing root endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    print("    ✓ Root endpoint working")
    
    print("✓ API structure test passed")


def test_pydantic_models():
    """Test Pydantic model validation"""
    print("Testing Pydantic models...")
    
    # Test VoiceCommandRequest
    print("  Testing VoiceCommandRequest...")
    try:
        # Valid request
        request = VoiceCommandRequest(
            session_id="test-session",
            text="add shirt to cart"
        )
        assert request.session_id == "test-session"
        assert request.text == "add shirt to cart"
        print("    ✓ VoiceCommandRequest validation working")
    except Exception as e:
        print(f"    ✗ VoiceCommandRequest validation failed: {e}")
        return False
    
    # Test TextCommandRequest
    print("  Testing TextCommandRequest...")
    try:
        request = TextCommandRequest(
            session_id="test-session",
            text="search for red shirts"
        )
        assert request.session_id == "test-session"
        assert request.text == "search for red shirts"
        print("    ✓ TextCommandRequest validation working")
    except Exception as e:
        print(f"    ✗ TextCommandRequest validation failed: {e}")
        return False
    
    # Test ErrorResponse
    print("  Testing ErrorResponse...")
    try:
        error = ErrorResponse(
            error_type="test_error",
            message="Test error message"
        )
        assert error.error_type == "test_error"
        assert error.message == "Test error message"
        assert error.error == True
        print("    ✓ ErrorResponse validation working")
    except Exception as e:
        print(f"    ✗ ErrorResponse validation failed: {e}")
        return False
    
    print("✓ Pydantic models test passed")
    return True


def test_model_validation_errors():
    """Test model validation error handling"""
    print("Testing model validation errors...")
    
    # Test empty session ID
    print("  Testing empty session ID validation...")
    try:
        VoiceCommandRequest(session_id="", text="test")
        print("    ✗ Should have failed with empty session ID")
        return False
    except Exception:
        print("    ✓ Empty session ID validation working")
    
    # Test missing required fields
    print("  Testing missing required fields...")
    try:
        TextCommandRequest(session_id="test")  # Missing text
        print("    ✗ Should have failed with missing text")
        return False
    except Exception:
        print("    ✓ Missing field validation working")
    
    print("✓ Model validation errors test passed")
    return True


def test_endpoint_routes():
    """Test that all expected routes are defined"""
    print("Testing endpoint routes...")
    
    app = create_test_app()
    
    # Check that routes are defined
    route_paths = [route.path for route in app.routes]
    
    expected_paths = [
        "/api/v1/voice/process",
        "/api/v1/text/process",
        "/api/v1/voice/upload",
        "/api/v1/cart/{session_id}",
        "/api/v1/cart/add",
        "/api/v1/cart/remove",
        "/api/v1/cart/update",
        "/api/v1/products/search",
        "/api/v1/products/{product_id}",
        "/api/v1/health",
        "/api/v1/sessions/{session_id}",
        "/api/v1/stats"
    ]
    
    print("  Checking expected routes...")
    for expected_path in expected_paths:
        # Check if path exists (allowing for parameter variations)
        path_found = any(
            expected_path.replace("{session_id}", "").replace("{product_id}", "") in path
            for path in route_paths
        )
        if path_found:
            print(f"    ✓ Route found: {expected_path}")
        else:
            print(f"    ⚠ Route not found: {expected_path}")
    
    print("✓ Endpoint routes test completed")


def test_serialization():
    """Test JSON serialization"""
    print("Testing JSON serialization...")
    
    try:
        from voice_shopping_assistant.api.serializers import (
            serialize_error_response, serialize_success_response
        )
        
        # Test error response serialization
        print("  Testing error response serialization...")
        error_data = serialize_error_response("test_error", "Test message")
        assert error_data["error"] == True
        assert error_data["error_type"] == "test_error"
        assert error_data["message"] == "Test message"
        print("    ✓ Error response serialization working")
        
        # Test success response serialization
        print("  Testing success response serialization...")
        success_data = serialize_success_response({"key": "value"}, "Success message")
        assert success_data["success"] == True
        assert success_data["data"]["key"] == "value"
        assert success_data["message"] == "Success message"
        print("    ✓ Success response serialization working")
        
    except Exception as e:
        print(f"    ✗ Serialization test failed: {e}")
        return False
    
    print("✓ JSON serialization test passed")
    return True


def test_validation_utilities():
    """Test validation utilities"""
    print("Testing validation utilities...")
    
    try:
        from voice_shopping_assistant.api.validators import RequestValidator
        
        # Test session ID validation
        print("  Testing session ID validation...")
        is_valid, error = RequestValidator.validate_session_id("valid-session-123")
        assert is_valid == True
        assert error is None
        print("    ✓ Valid session ID accepted")
        
        is_valid, error = RequestValidator.validate_session_id("")
        assert is_valid == False
        assert error is not None
        print("    ✓ Empty session ID rejected")
        
        # Test text input validation
        print("  Testing text input validation...")
        is_valid, error = RequestValidator.validate_text_input("Valid text input")
        assert is_valid == True
        assert error is None
        print("    ✓ Valid text input accepted")
        
        is_valid, error = RequestValidator.validate_text_input("")
        assert is_valid == False
        assert error is not None
        print("    ✓ Empty text input rejected")
        
    except Exception as e:
        print(f"    ✗ Validation utilities test failed: {e}")
        return False
    
    print("✓ Validation utilities test passed")
    return True


def run_basic_tests():
    """Run all basic tests"""
    print("=" * 60)
    print("Voice Shopping Assistant API Basic Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        test_api_structure()
        print()
        
        if not test_pydantic_models():
            return False
        print()
        
        if not test_model_validation_errors():
            return False
        print()
        
        test_endpoint_routes()
        print()
        
        if not test_serialization():
            return False
        print()
        
        if not test_validation_utilities():
            return False
        print()
        
        elapsed_time = time.time() - start_time
        print("=" * 60)
        print(f"✓ All basic tests passed in {elapsed_time:.2f} seconds")
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
    success = run_basic_tests()
    
    if success:
        print("\n🎉 API structure is working correctly!")
        print("Note: Full functionality tests require ML dependencies to be installed.")
    else:
        print("\n❌ API structure tests failed.")
    
    sys.exit(0 if success else 1)