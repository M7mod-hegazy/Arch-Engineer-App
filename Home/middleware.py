import time
import logging
import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

# Configure logger
logger = logging.getLogger('performance')

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health':
            logger.info(f"Health check intercepted - Method: {request.method}")
            response = HttpResponse(
                content="OK",
                status=200,
                content_type="text/plain",
                charset="utf-8"
            )
            response["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response
        return self.get_response(request)

class PerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to track request performance and log slow requests
    """
    def __init__(self, get_response=None):
        self.get_response = get_response
        # Default threshold for slow requests is 500ms
        self.threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD', 500)
        # Static file extensions to ignore
        self.ignore_pattern = re.compile(
            r'\.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot|map)$'
        )
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/')
        self.static_url = getattr(settings, 'STATIC_URL', '/static/')
        # Status logging for monitoring trends over time
        self.metrics = {
            'total_requests': 0,
            'slow_requests': 0,
            'total_time': 0,
        }

    def process_request(self, request):
        # Don't track static files or media files
        path = request.path_info
        if (path.startswith(self.static_url) or 
            path.startswith(self.media_url) or 
            self.ignore_pattern.search(path)):
            return None
            
        # Start tracking time
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        # Skip if we don't have a start time (static files etc.)
        if not hasattr(request, 'start_time'):
            return response
            
        # Calculate duration
        duration = time.time() - request.start_time
        duration_ms = int(duration * 1000)
        
        # Update metrics
        self.metrics['total_requests'] += 1
        self.metrics['total_time'] += duration
        
        # Add timing header
        response['X-Page-Generation-Duration-ms'] = str(duration_ms)
        
        # Log slow requests
        if duration_ms > self.threshold:
            self.metrics['slow_requests'] += 1
            logger.warning(
                'Slow request detected: %s %s %s (%dms) - User: %s',
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                request.user.username if request.user.is_authenticated else 'Anonymous'
            )
            
            # Log detail info for very slow requests (2x threshold)
            if duration_ms > (self.threshold * 2):
                logger.warning('Request details: %s', {
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                    'query_params': dict(request.GET),
                    'duration_ms': duration_ms,
                })
                
        # Log performance statistics every 100 requests
        if self.metrics['total_requests'] % 100 == 0:
            avg_time = self.metrics['total_time'] / self.metrics['total_requests'] * 1000
            slow_pct = (self.metrics['slow_requests'] / self.metrics['total_requests']) * 100
            logger.info(
                'Performance metrics: Requests: %d, Avg time: %.2fms, Slow: %.2f%%',
                self.metrics['total_requests'], 
                avg_time,
                slow_pct
            )
        
        return response

class DatabaseQueryCountMiddleware:
    """
    Middleware to count database queries per request.
    Requires Django Debug Toolbar or manual query counting.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.threshold = getattr(settings, 'QUERY_COUNT_THRESHOLD', 20)

    def __call__(self, request):
        # Skip for static/media files
        path = request.path_info
        if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
            return self.get_response(request)
            
        # Only activate in debug mode when we can count queries
        if not settings.DEBUG:
            return self.get_response(request)
        
        # Count database queries
        from django.db import connection
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        # Calculate query count
        final_queries = len(connection.queries)
        num_queries = final_queries - initial_queries
        
        # Log if over threshold
        if num_queries > self.threshold:
            logger.warning(
                'High query count detected: %s %s - %d queries',
                request.method, 
                request.path,
                num_queries
            )
            
            # Group similar queries for debugging
            if num_queries > (self.threshold * 2):
                from collections import defaultdict
                queries_by_type = defaultdict(int)
                
                for query in connection.queries[initial_queries:final_queries]:
                    # Simple classification by first keyword
                    query_type = query['sql'].split()[0].upper() if query['sql'] else 'UNKNOWN'
                    queries_by_type[query_type] += 1
                
                # Log query types
                logger.warning('Query breakdown: %s', dict(queries_by_type))
        
        # Add header in debug mode
        if settings.DEBUG:
            response['X-Query-Count'] = str(num_queries)
            
        return response

class CacheHeaderMiddleware:
    """
    Middleware to add appropriate cache headers based on request path
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Default cache durations (in seconds)
        self.cache_settings = {
            'static': 86400 * 30,  # 30 days for static files
            'media': 86400 * 7,    # 7 days for media files
            'api': 60,             # 1 minute for API responses
            'default': 0,          # No caching by default
        }
        
        # Override with settings if provided
        if hasattr(settings, 'CACHE_MIDDLEWARE_SETTINGS'):
            self.cache_settings.update(settings.CACHE_MIDDLEWARE_SETTINGS)
        
        # Regex patterns for different types of content
        self.patterns = {
            'static': re.compile(r'\.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$'),
            'media': re.compile(r'^/media/'),
            'api': re.compile(r'^/api/'),
        }

    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip for authenticated requests
        if request.user.is_authenticated:
            return response
        
        # Skip for POST, PUT, DELETE requests
        if request.method not in ('GET', 'HEAD'):
            return response
        
        # Determine type of content
        content_type = 'default'
        path = request.path_info
        
        if path.startswith(settings.STATIC_URL) or self.patterns['static'].search(path):
            content_type = 'static'
        elif self.patterns['media'].search(path):
            content_type = 'media'
        elif self.patterns['api'].search(path):
            content_type = 'api'
        
        # Get appropriate cache duration
        max_age = self.cache_settings.get(content_type, 0)
        
        # Add cache headers if duration > 0
        if max_age > 0:
            response['Cache-Control'] = f'public, max-age={max_age}'
            
            # For long-lived resources, add immutable directive
            if max_age > 86400:  # > 1 day
                response['Cache-Control'] += ', immutable'
        else:
            # Ensure no caching for dynamic content
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response

class HealthCheckLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health':
            logger.info(f"Health check request received - Method: {request.method}, Path: {request.path}")
        response = self.get_response(request)
        if request.path == '/health':
            logger.info(f"Health check response sent - Status: {response.status_code}")
        return response 