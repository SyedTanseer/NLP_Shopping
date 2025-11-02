"""Middleware for FastAPI application"""

import time
import logging
import json
from typing import Callable
from datetime import datetime

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .models import ErrorResponse
from .monitoring import get_performance_monitor
from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details"""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"({processing_time:.3f}s) "
                f"{request.method} {request.url.path}"
            )
            
            # Add processing time header
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}"
            
            # Record performance metrics
            try:
                monitor = get_performance_monitor()
                session_id = None
                
                # Try to extract session ID from request
                if hasattr(request, 'path_params') and 'session_id' in request.path_params:
                    session_id = request.path_params['session_id']
                elif request.method in ['POST', 'PUT', 'PATCH']:
                    # Try to get session_id from request body (if JSON)
                    try:
                        if hasattr(request, '_body'):
                            import json
                            body = json.loads(request._body.decode())
                            session_id = body.get('session_id')
                    except:
                        pass
                
                monitor.record_request(
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    processing_time=processing_time,
                    session_id=session_id
                )
            except Exception as monitor_error:
                logger.warning(f"Failed to record performance metrics: {monitor_error}")
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"({processing_time:.3f}s) - {str(e)}"
            )
            
            # Record error metrics
            try:
                monitor = get_performance_monitor()
                monitor.record_request(
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=500,
                    processing_time=processing_time,
                    error_type=type(e).__name__
                )
            except Exception as monitor_error:
                logger.warning(f"Failed to record error metrics: {monitor_error}")
            
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and exceptions"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors and return appropriate responses"""
        try:
            return await call_next(request)
            
        except HTTPException:
            # Let FastAPI handle HTTP exceptions
            raise
            
        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error: {str(e)}")
            error_response = ErrorResponse(
                error_type="validation_error",
                message=f"Invalid input: {str(e)}"
            )
            return JSONResponse(
                status_code=400,
                content=error_response.dict()
            )
            
        except FileNotFoundError as e:
            # Handle file not found errors
            logger.warning(f"File not found: {str(e)}")
            error_response = ErrorResponse(
                error_type="file_not_found",
                message="Requested resource not found"
            )
            return JSONResponse(
                status_code=404,
                content=error_response.dict()
            )
            
        except PermissionError as e:
            # Handle permission errors
            logger.warning(f"Permission error: {str(e)}")
            error_response = ErrorResponse(
                error_type="permission_error",
                message="Access denied"
            )
            return JSONResponse(
                status_code=403,
                content=error_response.dict()
            )
            
        except TimeoutError as e:
            # Handle timeout errors
            logger.warning(f"Timeout error: {str(e)}")
            error_response = ErrorResponse(
                error_type="timeout_error",
                message="Request timed out"
            )
            return JSONResponse(
                status_code=408,
                content=error_response.dict()
            )
            
        except Exception as e:
            # Handle all other exceptions
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            error_response = ErrorResponse(
                error_type="internal_error",
                message="An internal error occurred"
            )
            return JSONResponse(
                status_code=500,
                content=error_response.dict()
            )


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation and preprocessing"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.max_request_size = self.settings.api.max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request before processing"""
        
        # Check request size
        if hasattr(request, 'headers'):
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.max_request_size:
                error_response = ErrorResponse(
                    error_type="request_too_large",
                    message=f"Request too large (max {self.max_request_size} bytes)"
                )
                return JSONResponse(
                    status_code=413,
                    content=error_response.dict()
                )
        
        # Check content type for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('content-type', '')
            
            # Allow JSON and multipart form data
            if not (content_type.startswith('application/json') or 
                   content_type.startswith('multipart/form-data') or
                   content_type.startswith('application/x-www-form-urlencoded')):
                
                # Special handling for audio uploads
                if not (request.url.path.endswith('/upload') and 
                       content_type.startswith('audio/')):
                    error_response = ErrorResponse(
                        error_type="invalid_content_type",
                        message="Invalid content type"
                    )
                    return JSONResponse(
                        status_code=415,
                        content=error_response.dict()
                    )
        
        return await call_next(request)


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware"""
    
    def __init__(self, app: ASGIApp, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle CORS headers"""
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        origin = request.headers.get("origin")
        if origin and (self.allowed_origins == ["*"] or origin in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif self.allowed_origins == ["*"]:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # client_ip -> [(timestamp, count)]
        self.window_size = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting"""
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            error_response = ErrorResponse(
                error_type="rate_limit_exceeded",
                message=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
            return JSONResponse(
                status_code=429,
                content=error_response.dict(),
                headers={"Retry-After": "60"}
            )
        
        # Record request
        self._record_request(client_ip, current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries outside the time window"""
        cutoff_time = current_time - self.window_size
        
        for client_ip in list(self.request_counts.keys()):
            # Filter out old entries
            self.request_counts[client_ip] = [
                (timestamp, count) for timestamp, count in self.request_counts[client_ip]
                if timestamp > cutoff_time
            ]
            
            # Remove empty entries
            if not self.request_counts[client_ip]:
                del self.request_counts[client_ip]
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client is rate limited"""
        if client_ip not in self.request_counts:
            return False
        
        # Count requests in current window
        cutoff_time = current_time - self.window_size
        request_count = sum(
            count for timestamp, count in self.request_counts[client_ip]
            if timestamp > cutoff_time
        )
        
        return request_count >= self.requests_per_minute
    
    def _record_request(self, client_ip: str, current_time: float):
        """Record a request for the client"""
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        self.request_counts[client_ip].append((current_time, 1))


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add CSP header for API endpoints
        if request.url.path.startswith("/api/"):
            response.headers["Content-Security-Policy"] = "default-src 'none'"
        
        return response


def setup_middleware(app):
    """Setup all middleware for the FastAPI app"""
    settings = get_settings()
    
    # Add middleware in reverse order (last added is executed first)
    
    # Security headers (executed last)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # CORS handling
    app.add_middleware(CORSMiddleware, allowed_origins=settings.api.cors_origins)
    
    # Rate limiting
    if hasattr(settings.api, 'rate_limit_per_minute'):
        app.add_middleware(RateLimitingMiddleware, 
                          requests_per_minute=settings.api.rate_limit_per_minute)
    
    # Error handling
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Request validation
    app.add_middleware(RequestValidationMiddleware)
    
    # Request logging (executed first)
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Middleware setup completed")