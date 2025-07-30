from functools import wraps
from flask import request, make_response, current_app
import json
import hashlib
from app import redis_client

def cache_page(timeout=300):
    """Cache entire page responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_client:
                return f(*args, **kwargs)
            
            # Create cache key from URL and args
            cache_key = _make_cache_key(request.path, request.args)
            
            # Try to get from cache
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    response = make_response(cached.decode('utf-8'))
                    response.headers['X-Cache'] = 'HIT'
                    return response
            except:
                pass
            
            # Generate response
            response = make_response(f(*args, **kwargs))
            
            # Cache successful responses only
            if response.status_code == 200:
                try:
                    redis_client.setex(
                        cache_key,
                        timeout,
                        response.get_data(as_text=True)
                    )
                except:
                    pass
            
            response.headers['X-Cache'] = 'MISS'
            return response
        
        return decorated_function
    return decorator

def cache_calculation(timeout=3600):
    """Cache calculation results"""
    def decorator(f):
        @wraps(f)
        def decorated_function(self, inputs):
            if not redis_client:
                return f(self, inputs)
            
            # Create cache key from inputs
            cache_key = f"calc:{self.slug}:{_hash_dict(inputs)}"
            
            # Try cache first
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached.decode('utf-8'))
            except:
                pass
            
            # Calculate
            result = f(self, inputs)
            
            # Cache result
            try:
                redis_client.setex(
                    cache_key,
                    timeout,
                    json.dumps(result)
                )
            except:
                pass
            
            return result
        
        return decorated_function
    return decorator

def _make_cache_key(path, args):
    """Generate cache key from request"""
    key_parts = [path]
    for k, v in sorted(args.items()):
        key_parts.append(f"{k}={v}")
    return f"page:{':'.join(key_parts)}"

def _hash_dict(d):
    """Create hash from dictionary"""
    return hashlib.md5(
        json.dumps(d, sort_keys=True).encode()
    ).hexdigest()