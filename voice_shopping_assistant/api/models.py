"""Pydantic models for API request/response validation"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class IntentTypeAPI(str, Enum):
    """Intent types for API"""
    ADD = "add"
    REMOVE = "remove"
    SEARCH = "search"
    CHECKOUT = "checkout"
    HELP = "help"
    CANCEL = "cancel"


class EntityTypeAPI(str, Enum):
    """Entity types for API"""
    PRODUCT = "product"
    COLOR = "color"
    SIZE = "size"
    MATERIAL = "material"
    QUANTITY = "quantity"
    PRICE = "price"
    BRAND = "brand"


class VoiceCommandRequest(BaseModel):
    """Request model for voice command processing"""
    session_id: str = Field(..., description="User session identifier")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    text: Optional[str] = Field(None, description="Direct text input (for testing)")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Session ID cannot be empty')
        return v.strip()
    
    @validator('audio_data', 'text')
    def validate_input(cls, v, values):
        # At least one of audio_data or text must be provided
        if not values.get('audio_data') and not v:
            raise ValueError('Either audio_data or text must be provided')
        return v


class TextCommandRequest(BaseModel):
    """Request model for text command processing"""
    session_id: str = Field(..., description="User session identifier")
    text: str = Field(..., description="Text command to process")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Session ID cannot be empty')
        return v.strip()
    
    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Text cannot be empty')
        if len(v) > 500:
            raise ValueError('Text too long (max 500 characters)')
        return v.strip()


class EntityResponse(BaseModel):
    """Response model for entity data"""
    type: EntityTypeAPI
    value: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    span: List[int] = Field(..., description="Character positions [start, end]")
    is_high_confidence: bool
    is_valid_for_type: bool


class IntentResponse(BaseModel):
    """Response model for intent data"""
    type: IntentTypeAPI
    confidence: float = Field(..., ge=0.0, le=1.0)
    entities: List[EntityResponse]
    is_high_confidence: bool
    entity_count: int
    is_compatible: bool


class ProductResponse(BaseModel):
    """Response model for product data"""
    id: str
    name: str
    category: str
    price: float = Field(..., ge=0.0)
    available_sizes: List[str]
    available_colors: List[str]
    material: str
    brand: str
    in_stock: bool
    description: Optional[str] = None


class CartItemResponse(BaseModel):
    """Response model for cart item data"""
    product: ProductResponse
    quantity: int = Field(..., ge=1)
    size: Optional[str] = None
    color: Optional[str] = None
    unit_price: float = Field(..., ge=0.0)
    total_price: float = Field(..., ge=0.0)


class CartSummaryResponse(BaseModel):
    """Response model for cart summary data"""
    items: List[CartItemResponse]
    total_items: int = Field(..., ge=0)
    total_price: float = Field(..., ge=0.0)
    timestamp: str
    item_count: int = Field(..., ge=0)
    is_empty: bool


class ProcessingResultResponse(BaseModel):
    """Response model for complete processing result"""
    original_text: str
    normalized_text: str
    intent: IntentResponse
    entities: List[EntityResponse]
    response_text: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    processing_time: float = Field(..., ge=0.0)
    is_successful: bool
    performance_rating: str
    cart_summary: Optional[CartSummaryResponse] = None


class CartOperationRequest(BaseModel):
    """Request model for cart operations"""
    session_id: str = Field(..., description="User session identifier")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Session ID cannot be empty')
        return v.strip()


class AddItemRequest(CartOperationRequest):
    """Request model for adding items to cart"""
    items: List[Dict[str, Any]] = Field(..., description="Items to add")
    
    @validator('items')
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one item must be specified')
        if len(v) > 10:
            raise ValueError('Cannot add more than 10 items at once')
        return v


class RemoveItemRequest(CartOperationRequest):
    """Request model for removing items from cart"""
    criteria: Dict[str, Any] = Field(..., description="Removal criteria")
    
    @validator('criteria')
    def validate_criteria(cls, v):
        if not v:
            raise ValueError('Removal criteria must be specified')
        return v


class UpdateQuantityRequest(CartOperationRequest):
    """Request model for updating item quantity"""
    product_id: str = Field(..., description="Product ID to update")
    new_quantity: int = Field(..., ge=0, le=100, description="New quantity (0 to remove)")
    size: Optional[str] = None
    color: Optional[str] = None


class SearchProductsRequest(BaseModel):
    """Request model for product search"""
    query: Optional[str] = Field(None, description="Search query text")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    limit: int = Field(10, ge=1, le=50, description="Maximum results to return")
    
    @validator('query', 'filters')
    def validate_search_params(cls, v, values):
        # At least one of query or filters must be provided
        if not values.get('query') and not v:
            raise ValueError('Either query or filters must be provided')
        return v


class ProductSearchResponse(BaseModel):
    """Response model for product search results"""
    products: List[ProductResponse]
    total_found: int
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    processing_time: float = Field(..., ge=0.0)


class CartOperationResponse(BaseModel):
    """Response model for cart operations"""
    success: bool
    message: str
    cart_summary: Optional[CartSummaryResponse] = None
    processing_time: float = Field(..., ge=0.0)


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: bool = True
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"
    components: Dict[str, str]


class SessionInfoResponse(BaseModel):
    """Response model for session information"""
    session_id: str
    active_sessions: int
    cart_summary: Optional[CartSummaryResponse] = None
    last_activity: str
    session_duration: float


class APIStatsResponse(BaseModel):
    """Response model for API statistics"""
    total_requests: int
    successful_requests: int
    error_requests: int
    average_processing_time: float
    active_sessions: int
    uptime: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# Request/Response unions for flexibility
CommandRequest = Union[VoiceCommandRequest, TextCommandRequest]
APIResponse = Union[ProcessingResultResponse, CartOperationResponse, ProductSearchResponse, ErrorResponse]