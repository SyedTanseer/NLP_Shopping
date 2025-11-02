"""Performance monitoring and logging for API endpoints"""

import time
import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    processing_time: float
    session_id: Optional[str] = None
    error_type: Optional[str] = None


@dataclass
class EndpointStats:
    """Statistics for an endpoint"""
    total_requests: int = 0
    successful_requests: int = 0
    error_requests: int = 0
    total_processing_time: float = 0.0
    min_processing_time: float = float('inf')
    max_processing_time: float = 0.0
    recent_requests: deque = field(default_factory=lambda: deque(maxlen=100))
    error_types: Dict[str, int] = field(default_factory=dict)
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time"""
        if self.total_requests == 0:
            return 0.0
        return self.total_processing_time / self.total_requests
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.error_requests / self.total_requests) * 100


class PerformanceMonitor:
    """Monitor API performance and collect metrics"""
    
    def __init__(self, max_history_hours: int = 24):
        """Initialize performance monitor
        
        Args:
            max_history_hours: Maximum hours of history to keep
        """
        self.max_history_hours = max_history_hours
        self.start_time = datetime.now()
        
        # Thread-safe storage
        self._lock = threading.RLock()
        
        # Metrics storage
        self.endpoint_stats: Dict[str, EndpointStats] = defaultdict(EndpointStats)
        self.request_history: deque = deque(maxlen=10000)  # Last 10k requests
        self.session_metrics: Dict[str, List[RequestMetrics]] = defaultdict(list)
        
        # Performance thresholds
        self.slow_request_threshold = 2.0  # seconds
        self.error_rate_threshold = 5.0    # percentage
        
        # Alerts
        self.alerts: List[Dict[str, Any]] = []
        
        logger.info("Performance monitor initialized")
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      processing_time: float, session_id: Optional[str] = None,
                      error_type: Optional[str] = None):
        """Record a request for monitoring
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            status_code: HTTP status code
            processing_time: Request processing time in seconds
            session_id: Optional session identifier
            error_type: Optional error type for failed requests
        """
        with self._lock:
            # Create request metrics
            metrics = RequestMetrics(
                timestamp=datetime.now(),
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                processing_time=processing_time,
                session_id=session_id,
                error_type=error_type
            )
            
            # Add to history
            self.request_history.append(metrics)
            
            # Update endpoint statistics
            endpoint_key = f"{method} {endpoint}"
            stats = self.endpoint_stats[endpoint_key]
            
            stats.total_requests += 1
            stats.total_processing_time += processing_time
            stats.recent_requests.append(metrics)
            
            # Update min/max processing times
            stats.min_processing_time = min(stats.min_processing_time, processing_time)
            stats.max_processing_time = max(stats.max_processing_time, processing_time)
            
            # Update success/error counts
            if 200 <= status_code < 400:
                stats.successful_requests += 1
            else:
                stats.error_requests += 1
                if error_type:
                    stats.error_types[error_type] = stats.error_types.get(error_type, 0) + 1
            
            # Update session metrics
            if session_id:
                self.session_metrics[session_id].append(metrics)
                # Keep only recent session metrics
                if len(self.session_metrics[session_id]) > 100:
                    self.session_metrics[session_id] = self.session_metrics[session_id][-100:]
            
            # Check for performance issues
            self._check_performance_alerts(endpoint_key, stats, processing_time)
            
            # Cleanup old data
            self._cleanup_old_data()
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall API statistics"""
        with self._lock:
            total_requests = sum(stats.total_requests for stats in self.endpoint_stats.values())
            total_successful = sum(stats.successful_requests for stats in self.endpoint_stats.values())
            total_errors = sum(stats.error_requests for stats in self.endpoint_stats.values())
            total_processing_time = sum(stats.total_processing_time for stats in self.endpoint_stats.values())
            
            avg_processing_time = 0.0
            if total_requests > 0:
                avg_processing_time = total_processing_time / total_requests
            
            success_rate = 0.0
            if total_requests > 0:
                success_rate = (total_successful / total_requests) * 100
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "uptime_seconds": uptime,
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "error_requests": total_errors,
                "success_rate_percent": success_rate,
                "average_processing_time": avg_processing_time,
                "active_sessions": len(self.session_metrics),
                "endpoints_monitored": len(self.endpoint_stats),
                "recent_alerts": len([a for a in self.alerts if a['timestamp'] > datetime.now() - timedelta(hours=1)])
            }
    
    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for specific endpoint or all endpoints
        
        Args:
            endpoint: Optional endpoint to get stats for
            
        Returns:
            Dictionary of endpoint statistics
        """
        with self._lock:
            if endpoint:
                if endpoint in self.endpoint_stats:
                    stats = self.endpoint_stats[endpoint]
                    return {
                        "endpoint": endpoint,
                        "total_requests": stats.total_requests,
                        "successful_requests": stats.successful_requests,
                        "error_requests": stats.error_requests,
                        "success_rate_percent": stats.success_rate,
                        "error_rate_percent": stats.error_rate,
                        "average_processing_time": stats.average_processing_time,
                        "min_processing_time": stats.min_processing_time if stats.min_processing_time != float('inf') else 0.0,
                        "max_processing_time": stats.max_processing_time,
                        "error_types": dict(stats.error_types)
                    }
                else:
                    return {"error": f"Endpoint {endpoint} not found"}
            else:
                # Return all endpoint stats
                result = {}
                for endpoint_key, stats in self.endpoint_stats.items():
                    result[endpoint_key] = {
                        "total_requests": stats.total_requests,
                        "successful_requests": stats.successful_requests,
                        "error_requests": stats.error_requests,
                        "success_rate_percent": stats.success_rate,
                        "error_rate_percent": stats.error_rate,
                        "average_processing_time": stats.average_processing_time,
                        "min_processing_time": stats.min_processing_time if stats.min_processing_time != float('inf') else 0.0,
                        "max_processing_time": stats.max_processing_time,
                        "error_types": dict(stats.error_types)
                    }
                return result
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary of session statistics
        """
        with self._lock:
            if session_id not in self.session_metrics:
                return {"error": f"Session {session_id} not found"}
            
            session_requests = self.session_metrics[session_id]
            
            if not session_requests:
                return {"session_id": session_id, "total_requests": 0}
            
            total_requests = len(session_requests)
            successful_requests = sum(1 for r in session_requests if 200 <= r.status_code < 400)
            error_requests = total_requests - successful_requests
            total_processing_time = sum(r.processing_time for r in session_requests)
            
            avg_processing_time = total_processing_time / total_requests if total_requests > 0 else 0.0
            success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0.0
            
            # Session duration
            first_request = min(session_requests, key=lambda r: r.timestamp)
            last_request = max(session_requests, key=lambda r: r.timestamp)
            session_duration = (last_request.timestamp - first_request.timestamp).total_seconds()
            
            return {
                "session_id": session_id,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "error_requests": error_requests,
                "success_rate_percent": success_rate,
                "average_processing_time": avg_processing_time,
                "session_duration_seconds": session_duration,
                "first_request": first_request.timestamp.isoformat(),
                "last_request": last_request.timestamp.isoformat()
            }
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent requests
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of recent request data
        """
        with self._lock:
            recent = list(self.request_history)[-limit:]
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "status_code": r.status_code,
                    "processing_time": r.processing_time,
                    "session_id": r.session_id,
                    "error_type": r.error_type
                }
                for r in recent
            ]
    
    def get_slow_requests(self, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get requests that exceeded processing time threshold
        
        Args:
            threshold: Processing time threshold in seconds
            
        Returns:
            List of slow requests
        """
        threshold = threshold or self.slow_request_threshold
        
        with self._lock:
            slow_requests = [
                r for r in self.request_history
                if r.processing_time > threshold
            ]
            
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "processing_time": r.processing_time,
                    "session_id": r.session_id
                }
                for r in slow_requests[-100:]  # Last 100 slow requests
            ]
    
    def get_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent alerts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            recent_alerts = [
                alert for alert in self.alerts
                if alert['timestamp'] > cutoff_time
            ]
            
            return recent_alerts
    
    def _check_performance_alerts(self, endpoint: str, stats: EndpointStats, processing_time: float):
        """Check for performance issues and generate alerts"""
        
        # Check for slow requests
        if processing_time > self.slow_request_threshold:
            self._add_alert(
                "slow_request",
                f"Slow request detected: {endpoint} took {processing_time:.2f}s",
                {"endpoint": endpoint, "processing_time": processing_time}
            )
        
        # Check error rate (only if we have enough requests)
        if stats.total_requests >= 10 and stats.error_rate > self.error_rate_threshold:
            self._add_alert(
                "high_error_rate",
                f"High error rate detected: {endpoint} has {stats.error_rate:.1f}% error rate",
                {"endpoint": endpoint, "error_rate": stats.error_rate, "total_requests": stats.total_requests}
            )
    
    def _add_alert(self, alert_type: str, message: str, details: Dict[str, Any]):
        """Add an alert to the alerts list"""
        alert = {
            "timestamp": datetime.now(),
            "type": alert_type,
            "message": message,
            "details": details
        }
        
        self.alerts.append(alert)
        
        # Keep only recent alerts (last 1000)
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        logger.warning(f"Performance alert: {message}")
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent memory leaks"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_history_hours)
        
        # Clean up session metrics
        for session_id in list(self.session_metrics.keys()):
            session_requests = self.session_metrics[session_id]
            # Remove old requests
            recent_requests = [
                r for r in session_requests
                if r.timestamp > cutoff_time
            ]
            
            if recent_requests:
                self.session_metrics[session_id] = recent_requests
            else:
                # Remove empty sessions
                del self.session_metrics[session_id]
        
        # Clean up alerts
        self.alerts = [
            alert for alert in self.alerts
            if alert['timestamp'] > cutoff_time
        ]
    
    def reset_stats(self):
        """Reset all statistics (for testing)"""
        with self._lock:
            self.endpoint_stats.clear()
            self.request_history.clear()
            self.session_metrics.clear()
            self.alerts.clear()
            self.start_time = datetime.now()
            logger.info("Performance monitor statistics reset")


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def reset_performance_monitor():
    """Reset the global performance monitor (for testing)"""
    global _performance_monitor
    _performance_monitor = None