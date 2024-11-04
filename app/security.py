from functools import wraps
from flask import request, abort, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach
import hashlib
import hmac
import time
import os
from typing import Any, Callable, Dict, Union, List

def sanitize_input(data: Any) -> Any:
    """Sanitize user input."""
    if isinstance(data, str):
        return bleach.clean(data)
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(v) for v in data]
    return data
    
def generate_csrf_token() -> str:
    """Generate a CSRF token using the current hour."""
    return hmac.new(
        current_app.config['CSRF_SECRET_KEY'].encode(),
        msg=str(int(time.time()) // 3600).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

def validate_csrf_token() -> None:
    """Validate CSRF token."""
    token = request.headers.get('X-CSRF-Token')
    if not token:
        abort(403, 'CSRF token missing')
    
    expected = hmac.new(
        current_app.config['CSRF_SECRET_KEY'].encode(),
        msg=str(int(time.time()) // 3600).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(token, expected):
        abort(403, 'Invalid CSRF token')

def require_csrf(f: Callable) -> Callable:
    """CSRF protection decorator."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        validate_csrf_token()
        return f(*args, **kwargs)
    return decorated_function

# Initialize rate limiter with Redis storage
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', '6379')

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{redis_host}:{redis_port}",
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",
    default_limits=["100 per minute"]
)