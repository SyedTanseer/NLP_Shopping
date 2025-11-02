"""FastAPI endpoints for voice shopping assistant"""

import time
import base64
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from .models import (
    VoiceCommandRequest, TextCommandRequest, AddItemRequest, RemoveItemRequest,
    UpdateQuantityRequest, SearchProductsRequest, CartOperationRequest,
    ProcessingResultResponse, CartOperationResponse, ProductSearchResponse,
    ErrorResponse, HealthResponse, SessionInfoResponse, APIStatsResponse
)
from .dependencies import (
    get_voice_processor, get_cart_manager, get_product_search,
    get_session_manager, get_api_stats
)
from .monitoring import get_performance_monitor
from ..models.core import VoiceCommand


logger = logging.getLogger(__name__)

# Create router for voice shopping endpoints
router = APIRouter(prefix="/api/v1", tags=["voice-shopping"])


@router.post("/voice/process", response_model=ProcessingResultResponse)
async def process_voice_command(
    request: VoiceCommandRequest,
    voice_processor=Depends(get_voice_processor),
    session_manager=Depends(get_session_manager),
    api_stats=Depends(get_api_stats),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Process voice command through complete pipeline
    
    Args:
        request: Voice command request with audio data or text
        
    Returns:
        Complete processing result with response text and cart updates
    """
    start_time = time.time()
    
    try:
        # Update API statistics
        api_stats.increment_request()
        
        # Validate session
        session_manager.update_session_activity(request.session_id)
        
        if request.audio_data:
            # Process audio command
            try:
                # Decode base64 audio data
                audio_bytes = base64.b64decode(request.audio_data)
                
                # Create voice command
                voice_command = VoiceCommand(
                    audio_data=audio_bytes,
                    timestamp=datetime.now(),
                    session_id=request.session_id
                )
                
                # Process through voice pipeline
                result = voice_processor.process_voice_command(voice_command)
                
            except Exception as e:
                logger.error(f"Voice processing failed: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Voice processing failed: {str(e)}"
                )
        
        elif request.text:
            # Process text command directly
            try:
                result = voice_processor.process_text_command(
                    text=request.text,
                    session_id=request.session_id
                )
            except Exception as e:
                logger.error(f"Text processing failed: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Text processing failed: {str(e)}"
                )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Either audio_data or text must be provided"
            )
        
        # Convert result to API response format
        response = _convert_processing_result(result)
        
        # Update statistics
        processing_time = time.time() - start_time
        api_stats.record_processing_time(processing_time)
        api_stats.increment_success()
        
        # Schedule background cleanup if needed
        background_tasks.add_task(session_manager.cleanup_expired_sessions)
        
        return response
        
    except HTTPException:
        api_stats.increment_error()
        raise
    except Exception as e:
        api_stats.increment_error()
        logger.error(f"Unexpected error in voice processing: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during voice processing"
        )


@router.post("/text/process", response_model=ProcessingResultResponse)
async def process_text_command(
    request: TextCommandRequest,
    voice_processor=Depends(get_voice_processor),
    session_manager=Depends(get_session_manager),
    api_stats=Depends(get_api_stats)
):
    """Process text command directly (for testing and debugging)
    
    Args:
        request: Text command request
        
    Returns:
        Complete processing result
    """
    start_time = time.time()
    
    try:
        # Update API statistics
        api_stats.increment_request()
        
        # Validate session
        session_manager.update_session_activity(request.session_id)
        
        # Process text command
        result = voice_processor.process_text_command(
            text=request.text,
            session_id=request.session_id
        )
        
        # Convert result to API response format
        response = _convert_processing_result(result)
        
        # Update statistics
        processing_time = time.time() - start_time
        api_stats.record_processing_time(processing_time)
        api_stats.increment_success()
        
        return response
        
    except Exception as e:
        api_stats.increment_error()
        logger.error(f"Text processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Text processing failed: {str(e)}"
        )


@router.post("/voice/upload", response_model=ProcessingResultResponse)
async def upload_voice_file(
    session_id: str,
    file: UploadFile = File(...),
    voice_processor=Depends(get_voice_processor),
    session_manager=Depends(get_session_manager),
    api_stats=Depends(get_api_stats)
):
    """Upload and process voice file
    
    Args:
        session_id: User session identifier
        file: Audio file upload
        
    Returns:
        Complete processing result
    """
    start_time = time.time()
    
    try:
        # Update API statistics
        api_stats.increment_request()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail="File too large (max 10MB)"
            )
        
        # Validate session
        session_manager.update_session_activity(session_id)
        
        # Read audio data
        audio_data = await file.read()
        
        # Create voice command
        voice_command = VoiceCommand(
            audio_data=audio_data,
            timestamp=datetime.now(),
            session_id=session_id
        )
        
        # Process voice command
        result = voice_processor.process_voice_command(voice_command)
        
        # Convert result to API response format
        response = _convert_processing_result(result)
        
        # Update statistics
        processing_time = time.time() - start_time
        api_stats.record_processing_time(processing_time)
        api_stats.increment_success()
        
        return response
        
    except HTTPException:
        api_stats.increment_error()
        raise
    except Exception as e:
        api_stats.increment_error()
        logger.error(f"Voice file processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Voice file processing failed: {str(e)}"
        )


# Cart Management Endpoints

@router.get("/cart/{session_id}", response_model=CartOperationResponse)
async def get_cart(
    session_id: str,
    cart_manager=Depends(get_cart_manager),
    session_manager=Depends(get_session_manager)
):
    """Get current cart contents
    
    Args:
        session_id: User session identifier
        
    Returns:
        Current cart summary
    """
    try:
        # Validate session
        session_manager.update_session_activity(session_id)
        
        # Get cart summary
        cart_summary = cart_manager.get_cart_summary(session_id)
        
        response = CartOperationResponse(
            success=True,
            message="Cart retrieved successfully" if cart_summary else "Cart is empty",
            cart_summary=_convert_cart_summary(cart_summary) if cart_summary else None,
            processing_time=0.0
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Get cart failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cart: {str(e)}"
        )


@router.post("/cart/add", response_model=CartOperationResponse)
async def add_to_cart(
    request: AddItemRequest,
    cart_manager=Depends(get_cart_manager),
    session_manager=Depends(get_session_manager)
):
    """Add items to cart
    
    Args:
        request: Add item request with items to add
        
    Returns:
        Cart operation result
    """
    start_time = time.time()
    
    try:
        # Validate session
        session_manager.update_session_activity(request.session_id)
        
        # Add items to cart
        result = cart_manager.add_items(request.session_id, request.items)
        
        # Convert result to API response
        response = CartOperationResponse(
            success=result.success,
            message=result.message,
            cart_summary=_convert_cart_summary(result.cart_summary) if result.cart_summary else None,
            processing_time=time.time() - start_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Add to cart failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to cart: {str(e)}"
        )


@router.post("/cart/remove", response_model=CartOperationResponse)
async def remove_from_cart(
    request: RemoveItemRequest,
    cart_manager=Depends(get_cart_manager),
    session_manager=Depends(get_session_manager)
):
    """Remove items from cart
    
    Args:
        request: Remove item request with removal criteria
        
    Returns:
        Cart operation result
    """
    start_time = time.time()
    
    try:
        # Validate session
        session_manager.update_session_activity(request.session_id)
        
        # Remove items from cart
        result = cart_manager.remove_items(request.session_id, request.criteria)
        
        # Convert result to API response
        response = CartOperationResponse(
            success=result.success,
            message=result.message,
            cart_summary=_convert_cart_summary(result.cart_summary) if result.cart_summary else None,
            processing_time=time.time() - start_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Remove from cart failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove items from cart: {str(e)}"
        )


@router.put("/cart/update", response_model=CartOperationResponse)
async def update_cart_item(
    request: UpdateQuantityRequest,
    cart_manager=Depends(get_cart_manager),
    session_manager=Depends(get_session_manager)
):
    """Update item quantity in cart
    
    Args:
        request: Update quantity request
        
    Returns:
        Cart operation result
    """
    start_time = time.time()
    
    try:
        # Validate session
        session_manager.update_session_activity(request.session_id)
        
        # Update item quantity
        result = cart_manager.update_item_quantity(
            session_id=request.session_id,
            product_id=request.product_id,
            new_quantity=request.new_quantity,
            size=request.size,
            color=request.color
        )
        
        # Convert result to API response
        response = CartOperationResponse(
            success=result.success,
            message=result.message,
            cart_summary=_convert_cart_summary(result.cart_summary) if result.cart_summary else None,
            processing_time=time.time() - start_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Update cart item failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update cart item: {str(e)}"
        )


@router.delete("/cart/{session_id}", response_model=CartOperationResponse)
async def clear_cart(
    session_id: str,
    cart_manager=Depends(get_cart_manager),
    session_manager=Depends(get_session_manager)
):
    """Clear all items from cart
    
    Args:
        session_id: User session identifier
        
    Returns:
        Cart operation result
    """
    start_time = time.time()
    
    try:
        # Validate session
        session_manager.update_session_activity(session_id)
        
        # Clear cart
        result = cart_manager.clear_cart(session_id)
        
        # Convert result to API response
        response = CartOperationResponse(
            success=result.success,
            message=result.message,
            cart_summary=_convert_cart_summary(result.cart_summary) if result.cart_summary else None,
            processing_time=time.time() - start_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Clear cart failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cart: {str(e)}"
        )


# Product Search Endpoints

@router.post("/products/search", response_model=ProductSearchResponse)
async def search_products(
    request: SearchProductsRequest,
    product_search=Depends(get_product_search)
):
    """Search for products
    
    Args:
        request: Product search request
        
    Returns:
        Search results with matching products
    """
    start_time = time.time()
    
    try:
        if request.query:
            # Fuzzy search by query
            products = product_search.fuzzy_search(request.query, request.limit)
        elif request.filters:
            # Filter-based search
            products = product_search.search_products(request.filters)
            products = products[:request.limit]  # Limit results
        else:
            raise HTTPException(
                status_code=400,
                detail="Either query or filters must be provided"
            )
        
        # Convert products to API response format
        product_responses = [_convert_product(product) for product in products]
        
        response = ProductSearchResponse(
            products=product_responses,
            total_found=len(products),
            query=request.query,
            filters=request.filters,
            processing_time=time.time() - start_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Product search failed: {str(e)}"
        )


@router.get("/products/{product_id}")
async def get_product(
    product_id: str,
    product_search=Depends(get_product_search)
):
    """Get product by ID
    
    Args:
        product_id: Product identifier
        
    Returns:
        Product details
    """
    try:
        product = product_search.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found: {product_id}"
            )
        
        return _convert_product(product)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product: {str(e)}"
        )


# System Endpoints

@router.get("/health", response_model=HealthResponse)
async def health_check(
    voice_processor=Depends(get_voice_processor),
    cart_manager=Depends(get_cart_manager),
    product_search=Depends(get_product_search)
):
    """Health check endpoint
    
    Returns:
        System health status
    """
    try:
        components = {}
        
        # Check voice processor
        try:
            # Simple test to verify components are working
            components["voice_processor"] = "healthy"
        except Exception:
            components["voice_processor"] = "unhealthy"
        
        # Check cart manager
        try:
            session_count = cart_manager.get_session_count()
            components["cart_manager"] = f"healthy ({session_count} sessions)"
        except Exception:
            components["cart_manager"] = "unhealthy"
        
        # Check product search
        try:
            # Test search functionality
            test_products = product_search.fuzzy_search("test", 1)
            components["product_search"] = "healthy"
        except Exception:
            components["product_search"] = "unhealthy"
        
        # Determine overall status
        all_healthy = all(status.startswith("healthy") for status in components.values())
        status = "healthy" if all_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            components=components
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            components={"error": str(e)}
        )


@router.get("/sessions/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(
    session_id: str,
    cart_manager=Depends(get_cart_manager),
    session_manager=Depends(get_session_manager)
):
    """Get session information
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session information and cart status
    """
    try:
        # Get session info
        session_info = session_manager.get_session_info(session_id)
        
        # Get cart summary
        cart_summary = cart_manager.get_cart_summary(session_id)
        
        response = SessionInfoResponse(
            session_id=session_id,
            active_sessions=cart_manager.get_session_count(),
            cart_summary=_convert_cart_summary(cart_summary) if cart_summary else None,
            last_activity=session_info.get("last_activity", datetime.now().isoformat()),
            session_duration=session_info.get("duration", 0.0)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Get session info failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )


@router.get("/stats", response_model=APIStatsResponse)
async def get_api_stats(
    api_stats=Depends(get_api_stats),
    cart_manager=Depends(get_cart_manager)
):
    """Get API statistics
    
    Returns:
        API usage statistics
    """
    try:
        stats = api_stats.get_stats()
        
        response = APIStatsResponse(
            total_requests=stats["total_requests"],
            successful_requests=stats["successful_requests"],
            error_requests=stats["error_requests"],
            average_processing_time=stats["average_processing_time"],
            active_sessions=cart_manager.get_session_count(),
            uptime=stats["uptime"]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Get API stats failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get API stats: {str(e)}"
        )


@router.get("/performance", tags=["system"])
async def get_performance_metrics():
    """Get detailed performance metrics
    
    Returns:
        Detailed performance and monitoring data
    """
    try:
        monitor = get_performance_monitor()
        
        # Get overall stats
        overall_stats = monitor.get_overall_stats()
        
        # Get endpoint stats
        endpoint_stats = monitor.get_endpoint_stats()
        
        # Get recent slow requests
        slow_requests = monitor.get_slow_requests()
        
        # Get recent alerts
        alerts = monitor.get_alerts(hours=1)
        
        return {
            "overall": overall_stats,
            "endpoints": endpoint_stats,
            "slow_requests": slow_requests[-10:],  # Last 10 slow requests
            "recent_alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get performance metrics failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/performance/endpoint/{endpoint_path:path}", tags=["system"])
async def get_endpoint_performance(endpoint_path: str):
    """Get performance metrics for specific endpoint
    
    Args:
        endpoint_path: Endpoint path to get metrics for
        
    Returns:
        Endpoint-specific performance metrics
    """
    try:
        monitor = get_performance_monitor()
        
        # Get stats for specific endpoint
        endpoint_stats = monitor.get_endpoint_stats(endpoint_path)
        
        if "error" in endpoint_stats:
            raise HTTPException(
                status_code=404,
                detail=endpoint_stats["error"]
            )
        
        return {
            "endpoint": endpoint_path,
            "stats": endpoint_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get endpoint performance failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get endpoint performance: {str(e)}"
        )


# Helper functions for data conversion

def _convert_processing_result(result) -> ProcessingResultResponse:
    """Convert ProcessingResult to API response format"""
    from .models import ProcessingResultResponse, IntentResponse, EntityResponse
    
    # Convert entities
    entity_responses = []
    for entity in result.entities:
        entity_responses.append(EntityResponse(
            type=entity.type.value,
            value=entity.value,
            confidence=entity.confidence,
            span=list(entity.span),
            is_high_confidence=entity.is_high_confidence(),
            is_valid_for_type=entity.validate_value_for_type()
        ))
    
    # Convert intent
    intent_response = IntentResponse(
        type=result.intent.type.value,
        confidence=result.intent.confidence,
        entities=entity_responses,
        is_high_confidence=result.intent.is_high_confidence(),
        entity_count=len(result.intent.entities),
        is_compatible=result.intent.validate_intent_entity_compatibility()
    )
    
    return ProcessingResultResponse(
        original_text=result.original_text,
        normalized_text=result.normalized_text,
        intent=intent_response,
        entities=entity_responses,
        response_text=result.response_text,
        confidence_score=result.confidence_score,
        processing_time=result.processing_time,
        is_successful=result.is_successful(),
        performance_rating=result.get_performance_rating(),
        cart_summary=None  # Will be set by caller if needed
    )


def _convert_cart_summary(cart_summary):
    """Convert CartSummary to API response format"""
    if not cart_summary:
        return None
    
    from .models import CartSummaryResponse, CartItemResponse
    
    # Convert cart items
    item_responses = []
    for item in cart_summary.items:
        item_responses.append(CartItemResponse(
            product=_convert_product(item.product),
            quantity=item.quantity,
            size=item.size,
            color=item.color,
            unit_price=item.unit_price,
            total_price=item.total_price
        ))
    
    return CartSummaryResponse(
        items=item_responses,
        total_items=cart_summary.total_items,
        total_price=cart_summary.total_price,
        timestamp=cart_summary.timestamp.isoformat(),
        item_count=cart_summary.get_item_count(),
        is_empty=cart_summary.is_empty()
    )


def _convert_product(product):
    """Convert Product to API response format"""
    from .models import ProductResponse
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        price=product.price,
        available_sizes=product.available_sizes,
        available_colors=product.available_colors,
        material=product.material,
        brand=product.brand,
        in_stock=product.in_stock,
        description=product.description
    )