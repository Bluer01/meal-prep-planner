import time
import logging
from typing import Any
from flask import Flask, request, g

logger = logging.getLogger(__name__)

def init_middleware(app: Flask) -> None:
    """Initialize all middleware for the application."""
    
    @app.before_request
    def before_request() -> None:
        g.start_time = time.time()
        
    @app.after_request
    def after_request(response: Any) -> Any:
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            logger.info(
                f"Request: {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {elapsed:.2f}s"
            )
        return response