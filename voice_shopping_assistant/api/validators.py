"""Request validation utilities for API endpoints"""

import re
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from pydantic import ValidationError


class RequestValidator:
    """Utility class for request validation"""
    
    @staticmethod
    def validate_session_id(session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate session ID format
        
        Args:
            session_id: Session identifier to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not session_id:
            return False, "Session ID is required"
        
        if not isinstance(session_id, str):
            return False, "Session ID must be a string"
        
        session_id = session_id.strip()
        if not session_id:
            return False, "Session ID cannot be empty"
        
        if len(session_id) > 100:
            return False, "Session ID too long (max 100 characters)"
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            return False, "Session ID contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_audio_data(audio_data: str) -> Tuple[bool, Optional[str], Optional[bytes]]:
        """Validate base64 encoded audio data
        
        Args:
            audio_data: Base64 encoded audio string
            
        Returns:
            Tuple of (is_valid, error_message, decoded_bytes)
        """
        if not audio_data:
            return False, "Audio data is required", None
        
        if not isinstance(audio_data, str):
            return False, "Audio data must be a string", None
        
        # Check length (10MB limit when base64 encoded)
        max_encoded_size = 14 * 1024 * 1024  # ~10MB when decoded
        if len(audio_data) > max_encoded_size:
            return False, "Audio data too large (max 10MB)", None
        
        # Validate base64 format
        try:
            # Remove data URL prefix if present
            if audio_data.startswith('data:'):
                if ',' in audio_data:
                    audio_data = audio_data.split(',', 1)[1]
            
            # Decode base64
            decoded_bytes = base64.b64decode(audio_data, validate=True)
            
            # Check minimum size (at least 100 bytes)
            if len(decoded_bytes) < 100:
                return False, "Audio data too small", None
            
            return True, None, decoded_bytes
            
        except Exception as e:
            return False, f"Invalid base64 audio data: {str(e)}", None
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = 500) -> Tuple[bool, Optional[str]]:
        """Validate text input
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "Text is required"
        
        if not isinstance(text, str):
            return False, "Text must be a string"
        
        text = text.strip()
        if not text:
            return False, "Text cannot be empty"
        
        if len(text) > max_length:
            return False, f"Text too long (max {max_length} characters)"
        
        # Check for potentially malicious content
        suspicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'exec\s*\('
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Text contains potentially malicious content"
        
        return True, None
    
    @staticmethod
    def validate_product_filters(filters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate product search filters
        
        Args:
            filters: Dictionary of search filters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filters:
            return False, "Filters cannot be empty"
        
        if not isinstance(filters, dict):
            return False, "Filters must be a dictionary"
        
        # Validate allowed filter keys
        allowed_keys = {
            'category', 'brand', 'material', 'color', 'size',
            'min_price', 'max_price', 'in_stock', 'name'
        }
        
        invalid_keys = set(filters.keys()) - allowed_keys
        if invalid_keys:
            return False, f"Invalid filter keys: {', '.join(invalid_keys)}"
        
        # Validate price filters
        if 'min_price' in filters:
            try:
                min_price = float(filters['min_price'])
                if min_price < 0:
                    return False, "Minimum price cannot be negative"
            except (ValueError, TypeError):
                return False, "Invalid minimum price format"
        
        if 'max_price' in filters:
            try:
                max_price = float(filters['max_price'])
                if max_price < 0:
                    return False, "Maximum price cannot be negative"
            except (ValueError, TypeError):
                return False, "Invalid maximum price format"
        
        # Validate price range
        if 'min_price' in filters and 'max_price' in filters:
            min_price = float(filters['min_price'])
            max_price = float(filters['max_price'])
            if min_price > max_price:
                return False, "Minimum price cannot be greater than maximum price"
        
        # Validate string filters
        string_filters = ['category', 'brand', 'material', 'color', 'size', 'name']
        for key in string_filters:
            if key in filters:
                value = filters[key]
                if not isinstance(value, str):
                    return False, f"{key} must be a string"
                if len(value.strip()) == 0:
                    return False, f"{key} cannot be empty"
                if len(value) > 100:
                    return False, f"{key} too long (max 100 characters)"
        
        # Validate boolean filters
        if 'in_stock' in filters:
            if not isinstance(filters['in_stock'], bool):
                return False, "in_stock must be a boolean"
        
        return True, None
    
    @staticmethod
    def validate_cart_item_spec(item_spec: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate cart item specification
        
        Args:
            item_spec: Item specification dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not item_spec:
            return False, "Item specification is required"
        
        if not isinstance(item_spec, dict):
            return False, "Item specification must be a dictionary"
        
        # Check required fields
        required_fields = ['product_id']
        for field in required_fields:
            if field not in item_spec:
                return False, f"Missing required field: {field}"
        
        # Validate product_id
        product_id = item_spec['product_id']
        if not isinstance(product_id, str) or not product_id.strip():
            return False, "Product ID must be a non-empty string"
        
        # Validate quantity
        if 'quantity' in item_spec:
            try:
                quantity = int(item_spec['quantity'])
                if quantity <= 0:
                    return False, "Quantity must be positive"
                if quantity > 100:
                    return False, "Quantity cannot exceed 100"
            except (ValueError, TypeError):
                return False, "Invalid quantity format"
        
        # Validate optional string fields
        optional_string_fields = ['size', 'color']
        for field in optional_string_fields:
            if field in item_spec:
                value = item_spec[field]
                if value is not None:
                    if not isinstance(value, str):
                        return False, f"{field} must be a string"
                    if len(value.strip()) == 0:
                        return False, f"{field} cannot be empty"
                    if len(value) > 50:
                        return False, f"{field} too long (max 50 characters)"
        
        return True, None
    
    @staticmethod
    def validate_removal_criteria(criteria: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate item removal criteria
        
        Args:
            criteria: Removal criteria dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not criteria:
            return False, "Removal criteria is required"
        
        if not isinstance(criteria, dict):
            return False, "Removal criteria must be a dictionary"
        
        # Validate allowed criteria keys
        allowed_keys = {
            'product_id', 'product_name', 'color', 'size', 'quantity'
        }
        
        invalid_keys = set(criteria.keys()) - allowed_keys
        if invalid_keys:
            return False, f"Invalid criteria keys: {', '.join(invalid_keys)}"
        
        # At least one criterion must be specified
        if not any(criteria.values()):
            return False, "At least one removal criterion must be specified"
        
        # Validate string criteria
        string_criteria = ['product_id', 'product_name', 'color', 'size']
        for key in string_criteria:
            if key in criteria and criteria[key] is not None:
                value = criteria[key]
                if not isinstance(value, str):
                    return False, f"{key} must be a string"
                if len(value.strip()) == 0:
                    return False, f"{key} cannot be empty"
                if len(value) > 100:
                    return False, f"{key} too long (max 100 characters)"
        
        # Validate quantity
        if 'quantity' in criteria and criteria['quantity'] is not None:
            try:
                quantity = int(criteria['quantity'])
                if quantity <= 0:
                    return False, "Quantity must be positive"
            except (ValueError, TypeError):
                return False, "Invalid quantity format"
        
        return True, None
    
    @staticmethod
    def validate_file_upload(file_data: bytes, content_type: str) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file
        
        Args:
            file_data: File content bytes
            content_type: MIME content type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_data:
            return False, "File data is required"
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if len(file_data) > max_size:
            return False, f"File too large (max {max_size} bytes)"
        
        # Check minimum size
        if len(file_data) < 100:
            return False, "File too small"
        
        # Validate content type
        if not content_type:
            return False, "Content type is required"
        
        allowed_audio_types = [
            'audio/wav', 'audio/wave', 'audio/x-wav',
            'audio/mpeg', 'audio/mp3',
            'audio/ogg', 'audio/webm',
            'audio/flac', 'audio/aac'
        ]
        
        if content_type not in allowed_audio_types:
            return False, f"Unsupported audio format: {content_type}"
        
        # Basic file header validation
        if content_type.startswith('audio/wav') or content_type.startswith('audio/wave'):
            # Check for WAV header
            if not file_data.startswith(b'RIFF') or b'WAVE' not in file_data[:12]:
                return False, "Invalid WAV file format"
        
        return True, None
    
    @staticmethod
    def validate_pagination_params(page: int, page_size: int) -> Tuple[bool, Optional[str]]:
        """Validate pagination parameters
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if page < 1:
            return False, "Page number must be at least 1"
        
        if page > 1000:
            return False, "Page number too large (max 1000)"
        
        if page_size < 1:
            return False, "Page size must be at least 1"
        
        if page_size > 100:
            return False, "Page size too large (max 100)"
        
        return True, None


def validate_pydantic_model(model_class, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Any]]:
    """Validate data against Pydantic model
    
    Args:
        model_class: Pydantic model class
        data: Data to validate
        
    Returns:
        Tuple of (is_valid, error_message, model_instance)
    """
    try:
        model_instance = model_class(**data)
        return True, None, model_instance
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = '.'.join(str(loc) for loc in error['loc'])
            message = error['msg']
            error_messages.append(f"{field}: {message}")
        
        return False, '; '.join(error_messages), None
    except Exception as e:
        return False, f"Validation error: {str(e)}", None


def sanitize_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data to prevent injection attacks
    
    Args:
        data: Input data dictionary
        
    Returns:
        Sanitized data dictionary
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            sanitized_value = re.sub(r'[<>"\']', '', value)
            # Limit length
            sanitized_value = sanitized_value[:1000]
            sanitized[key] = sanitized_value
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_input_data(value)
        elif isinstance(value, list):
            # Sanitize list items
            sanitized_list = []
            for item in value[:100]:  # Limit list size
                if isinstance(item, dict):
                    sanitized_list.append(sanitize_input_data(item))
                elif isinstance(item, str):
                    sanitized_list.append(re.sub(r'[<>"\']', '', item)[:1000])
                else:
                    sanitized_list.append(item)
            sanitized[key] = sanitized_list
        else:
            sanitized[key] = value
    
    return sanitized