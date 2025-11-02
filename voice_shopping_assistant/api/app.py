"""Main FastAPI application for voice shopping assistant"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .endpoints import router
from .middleware import setup_middleware
from .models import ErrorResponse
from .dependencies import get_voice_processor, get_api_stats
from ..config.settings import get_settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Voice Shopping Assistant API...")
    
    try:
        # Initialize core components
        voice_processor = get_voice_processor()
        api_stats = get_api_stats()
        
        logger.info("All components initialized successfully")
        logger.info("Voice Shopping Assistant API is ready")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Voice Shopping Assistant API...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="Voice Shopping Assistant API",
        description="REST API for voice-enabled shopping assistant with natural language processing",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        debug=settings.api.debug
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Include API routes
    app.include_router(router)
    
    # Add root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information"""
        return {
            "name": "Voice Shopping Assistant API",
            "version": "1.0.0",
            "description": "REST API for voice-enabled shopping with NLP",
            "endpoints": {
                "docs": "/docs",
                "health": "/api/v1/health",
                "voice_processing": "/api/v1/voice/process",
                "text_processing": "/api/v1/text/process",
                "cart_management": "/api/v1/cart/",
                "product_search": "/api/v1/products/search"
            },
            "status": "running"
        }
    
    # Add custom exception handlers
    setup_exception_handlers(app)
    
    # Customize OpenAPI schema
    setup_openapi_schema(app)
    
    return app


def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers"""
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Handle 404 errors"""
        error_response = ErrorResponse(
            error_type="not_found",
            message=f"Endpoint not found: {request.url.path}"
        )
        return JSONResponse(
            status_code=404,
            content=error_response.dict()
        )
    
    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc):
        """Handle 405 errors"""
        error_response = ErrorResponse(
            error_type="method_not_allowed",
            message=f"Method {request.method} not allowed for {request.url.path}"
        )
        return JSONResponse(
            status_code=405,
            content=error_response.dict()
        )
    
    @app.exception_handler(422)
    async def validation_error_handler(request: Request, exc):
        """Handle validation errors"""
        error_response = ErrorResponse(
            error_type="validation_error",
            message="Request validation failed",
            details={"errors": exc.errors()} if hasattr(exc, 'errors') else None
        )
        return JSONResponse(
            status_code=422,
            content=error_response.dict()
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        """Handle internal server errors"""
        logger.error(f"Internal server error: {exc}", exc_info=True)
        error_response = ErrorResponse(
            error_type="internal_error",
            message="An internal server error occurred"
        )
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )


def setup_openapi_schema(app: FastAPI):
    """Customize OpenAPI schema"""
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="Voice Shopping Assistant API",
            version="1.0.0",
            description="""
            ## Voice Shopping Assistant API
            
            A comprehensive REST API for voice-enabled shopping with natural language processing capabilities.
            
            ### Features
            - **Voice Command Processing**: Convert speech to shopping actions
            - **Text Command Processing**: Direct text input for testing and integration
            - **Cart Management**: Add, remove, update, and view cart items
            - **Product Search**: Search and filter products with various criteria
            - **Session Management**: Maintain conversation context across requests
            - **Real-time Processing**: Fast response times with performance monitoring
            
            ### Authentication
            Currently, the API uses session-based identification. Include a `session_id` in your requests
            to maintain conversation context and cart state.
            
            ### Rate Limiting
            The API implements rate limiting to ensure fair usage. Default limit is 60 requests per minute
            per IP address.
            
            ### Error Handling
            All endpoints return standardized error responses with appropriate HTTP status codes and
            descriptive error messages.
            
            ### Audio Formats
            Supported audio formats for voice processing:
            - WAV (recommended)
            - MP3
            - OGG
            - WebM
            - FLAC
            - AAC
            
            Maximum file size: 10MB
            """,
            routes=app.routes,
        )
        
        # Add custom schema information
        openapi_schema["info"]["contact"] = {
            "name": "Voice Shopping Assistant API",
            "email": "support@voiceshopping.com"
        }
        
        openapi_schema["info"]["license"] = {
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        }
        
        # Add server information
        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.voiceshopping.com",
                "description": "Production server"
            }
        ]
        
        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "SessionAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Session-ID",
                "description": "Session identifier for maintaining conversation context"
            }
        }
        
        # Add tags
        openapi_schema["tags"] = [
            {
                "name": "voice-processing",
                "description": "Voice command processing endpoints"
            },
            {
                "name": "text-processing", 
                "description": "Text command processing endpoints"
            },
            {
                "name": "cart-management",
                "description": "Shopping cart management endpoints"
            },
            {
                "name": "product-search",
                "description": "Product search and catalog endpoints"
            },
            {
                "name": "system",
                "description": "System health and monitoring endpoints"
            }
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi


# Create the FastAPI application instance
app = create_app()


# Add startup event for additional initialization
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    logger.info("Performing additional startup tasks...")
    
    # Log configuration
    settings = get_settings()
    logger.info(f"API Configuration:")
    logger.info(f"  Host: {settings.api.host}")
    logger.info(f"  Port: {settings.api.port}")
    logger.info(f"  Debug: {settings.api.debug}")
    logger.info(f"  CORS Origins: {settings.api.cors_origins}")
    logger.info(f"  Max Request Size: {settings.api.max_request_size}")
    
    # Test component initialization
    try:
        voice_processor = get_voice_processor()
        logger.info("✓ Voice processor initialized")
        
        # Test basic functionality
        test_result = voice_processor.process_text_command("test", "startup-test")
        logger.info("✓ Basic processing test passed")
        
    except Exception as e:
        logger.error(f"✗ Component initialization failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks on shutdown"""
    logger.info("Performing cleanup tasks...")
    
    try:
        # Get final statistics
        api_stats = get_api_stats()
        stats = api_stats.get_stats()
        
        logger.info("Final API Statistics:")
        logger.info(f"  Total Requests: {stats['total_requests']}")
        logger.info(f"  Successful Requests: {stats['successful_requests']}")
        logger.info(f"  Error Requests: {stats['error_requests']}")
        logger.info(f"  Average Processing Time: {stats['average_processing_time']:.3f}s")
        logger.info(f"  Uptime: {stats['uptime']:.1f}s")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Voice Shopping Assistant API shutdown complete")


# Health check endpoint for load balancers
@app.get("/ping", tags=["system"])
async def ping():
    """Simple ping endpoint for health checks"""
    return {"status": "ok", "timestamp": time.time()}


# Metrics endpoint for monitoring
@app.get("/metrics", tags=["system"])
async def metrics():
    """Basic metrics endpoint"""
    try:
        api_stats = get_api_stats()
        stats = api_stats.get_stats()
        
        return {
            "status": "healthy",
            "metrics": {
                "requests_total": stats['total_requests'],
                "requests_successful": stats['successful_requests'],
                "requests_failed": stats['error_requests'],
                "processing_time_avg": stats['average_processing_time'],
                "uptime_seconds": stats['uptime']
            }
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    # Run the application
    uvicorn.run(
        "voice_shopping_assistant.api.app:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level="info" if not settings.api.debug else "debug",
        access_log=True
    )