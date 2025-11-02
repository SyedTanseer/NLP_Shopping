"""JSON serialization utilities for API responses"""

import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Union
from enum import Enum

from ..models.core import (
    Product, CartItem, CartSummary, Entity, Intent, 
    TranscriptionResult, NLPResult, ProcessingResult
)


class APIJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for API responses"""
    
    def default(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format"""
        
        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # Handle date objects
        if isinstance(obj, date):
            return obj.isoformat()
        
        # Handle Decimal objects
        if isinstance(obj, Decimal):
            return float(obj)
        
        # Handle Enum objects
        if isinstance(obj, Enum):
            return obj.value
        
        # Handle core model objects
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        # Handle sets
        if isinstance(obj, set):
            return list(obj)
        
        # Handle bytes
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        
        # Let the base class handle other types
        return super().default(obj)


def serialize_product(product: Product) -> Dict[str, Any]:
    """Serialize Product object to dictionary"""
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": float(product.price),
        "available_sizes": product.available_sizes,
        "available_colors": product.available_colors,
        "material": product.material,
        "brand": product.brand,
        "in_stock": product.in_stock,
        "description": product.description
    }


def serialize_cart_item(cart_item: CartItem) -> Dict[str, Any]:
    """Serialize CartItem object to dictionary"""
    return {
        "product": serialize_product(cart_item.product),
        "quantity": cart_item.quantity,
        "size": cart_item.size,
        "color": cart_item.color,
        "unit_price": float(cart_item.unit_price),
        "total_price": float(cart_item.total_price)
    }


def serialize_cart_summary(cart_summary: CartSummary) -> Dict[str, Any]:
    """Serialize CartSummary object to dictionary"""
    return {
        "items": [serialize_cart_item(item) for item in cart_summary.items],
        "total_items": cart_summary.total_items,
        "total_price": float(cart_summary.total_price),
        "timestamp": cart_summary.timestamp.isoformat(),
        "item_count": cart_summary.get_item_count(),
        "is_empty": cart_summary.is_empty()
    }


def serialize_entity(entity: Entity) -> Dict[str, Any]:
    """Serialize Entity object to dictionary"""
    return {
        "type": entity.type.value,
        "value": entity.value,
        "confidence": float(entity.confidence),
        "span": list(entity.span),
        "is_high_confidence": entity.is_high_confidence(),
        "is_valid_for_type": entity.validate_value_for_type()
    }


def serialize_intent(intent: Intent) -> Dict[str, Any]:
    """Serialize Intent object to dictionary"""
    return {
        "type": intent.type.value,
        "confidence": float(intent.confidence),
        "entities": [serialize_entity(entity) for entity in intent.entities],
        "is_high_confidence": intent.is_high_confidence(),
        "entity_count": len(intent.entities),
        "is_compatible": intent.validate_intent_entity_compatibility()
    }


def serialize_transcription_result(result: TranscriptionResult) -> Dict[str, Any]:
    """Serialize TranscriptionResult object to dictionary"""
    return {
        "text": result.text,
        "confidence": float(result.confidence),
        "processing_time": float(result.processing_time)
    }


def serialize_nlp_result(result: NLPResult) -> Dict[str, Any]:
    """Serialize NLPResult object to dictionary"""
    return {
        "original_text": result.original_text,
        "normalized_text": result.normalized_text,
        "intent": serialize_intent(result.intent),
        "entities": [serialize_entity(entity) for entity in result.entities],
        "confidence_score": float(result.confidence_score),
        "processing_quality": result.get_processing_quality(),
        "is_reliable": result.is_reliable(),
        "requires_clarification": result.requires_clarification()
    }


def serialize_processing_result(result: ProcessingResult) -> Dict[str, Any]:
    """Serialize ProcessingResult object to dictionary"""
    return {
        "original_text": result.original_text,
        "normalized_text": result.normalized_text,
        "intent": serialize_intent(result.intent),
        "entities": [serialize_entity(entity) for entity in result.entities],
        "response_text": result.response_text,
        "confidence_score": float(result.confidence_score),
        "processing_time": float(result.processing_time),
        "is_successful": result.is_successful(),
        "performance_rating": result.get_performance_rating()
    }


def serialize_error_response(error_type: str, message: str, 
                           details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Serialize error response"""
    response = {
        "error": True,
        "error_type": error_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        response["details"] = details
    
    return response


def serialize_success_response(data: Any, message: str = None) -> Dict[str, Any]:
    """Serialize success response"""
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    if message:
        response["message"] = message
    
    return response


def serialize_paginated_response(items: List[Any], total_count: int, 
                                page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Serialize paginated response"""
    return {
        "items": items,
        "pagination": {
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "has_next": page * page_size < total_count,
            "has_previous": page > 1
        },
        "timestamp": datetime.now().isoformat()
    }


class ResponseSerializer:
    """Utility class for response serialization"""
    
    @staticmethod
    def serialize_object(obj: Any) -> Dict[str, Any]:
        """Serialize any object to dictionary"""
        if isinstance(obj, Product):
            return serialize_product(obj)
        elif isinstance(obj, CartItem):
            return serialize_cart_item(obj)
        elif isinstance(obj, CartSummary):
            return serialize_cart_summary(obj)
        elif isinstance(obj, Entity):
            return serialize_entity(obj)
        elif isinstance(obj, Intent):
            return serialize_intent(obj)
        elif isinstance(obj, TranscriptionResult):
            return serialize_transcription_result(obj)
        elif isinstance(obj, NLPResult):
            return serialize_nlp_result(obj)
        elif isinstance(obj, ProcessingResult):
            return serialize_processing_result(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return obj
        elif isinstance(obj, list):
            return [ResponseSerializer.serialize_object(item) for item in obj]
        else:
            return obj
    
    @staticmethod
    def create_api_response(data: Any = None, message: str = None, 
                           error: str = None, status_code: int = 200) -> Dict[str, Any]:
        """Create standardized API response"""
        response = {
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code
        }
        
        if error:
            response.update({
                "success": False,
                "error": error,
                "data": None
            })
        else:
            response.update({
                "success": True,
                "error": None,
                "data": ResponseSerializer.serialize_object(data) if data is not None else None
            })
        
        if message:
            response["message"] = message
        
        return response
    
    @staticmethod
    def create_validation_error_response(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create validation error response"""
        return {
            "success": False,
            "error": "validation_error",
            "message": "Request validation failed",
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_not_found_response(resource: str, identifier: str = None) -> Dict[str, Any]:
        """Create not found error response"""
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        return {
            "success": False,
            "error": "not_found",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_server_error_response(message: str = "Internal server error") -> Dict[str, Any]:
        """Create server error response"""
        return {
            "success": False,
            "error": "server_error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }


def format_api_response(data: Any, encoder_class=APIJSONEncoder) -> str:
    """Format data as JSON API response"""
    return json.dumps(data, cls=encoder_class, ensure_ascii=False, indent=2)


def parse_api_request(json_str: str) -> Dict[str, Any]:
    """Parse JSON API request"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")


def validate_json_schema(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate JSON data against required fields"""
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None:
            errors.append(f"Field cannot be null: {field}")
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f"Field cannot be empty: {field}")
    
    return errors


def sanitize_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize JSON data by removing/cleaning problematic values"""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Strip whitespace and limit length
            sanitized[key] = value.strip()[:1000]
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_json_data(value)
        elif isinstance(value, list):
            # Sanitize list items
            sanitized[key] = [
                sanitize_json_data(item) if isinstance(item, dict) else item
                for item in value[:100]  # Limit list size
            ]
        else:
            sanitized[key] = value
    
    return sanitized