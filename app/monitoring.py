import time
from functools import wraps
from datetime import datetime
from app.models import PerformanceLog

def monitor_performance(action_name):
    """Decorator to monitor function performance"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                duration = time.time() - start_time
                
                # Log if slow (over 1 second)
                if duration > 1.0:
                    try:
                        PerformanceLog.create(
                            action=action_name,
                            duration=duration,
                            timestamp=datetime.utcnow()
                        )
                    except:
                        pass  # Don't let logging errors break the function
                
                return result
                
            except Exception as e:
                # Log errors with duration
                duration = time.time() - start_time
                try:
                    PerformanceLog.create(
                        action=f"{action_name}_ERROR",
                        duration=duration,
                        timestamp=datetime.utcnow()
                    )
                except:
                    pass
                
                raise e
        
        return decorated_function
    return decorator

def log_page_performance(request, response, render_time):
    """Log page load performance"""
    try:
        # Only log slow pages (over 2 seconds)
        if render_time > 2.0:
            PerformanceLog.create(
                action=f"SLOW_PAGE:{request.path}",
                duration=render_time,
                timestamp=datetime.utcnow()
            )
    except:
        pass