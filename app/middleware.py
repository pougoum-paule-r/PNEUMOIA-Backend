"""
Middleware for request/response handling, logging, and CORS.
"""
import logging
import time
from typing import Callable

from fastapi import Request
from fastapi.responses import Response

logger = logging.getLogger(__name__)


async def log_request_middleware(request: Request, call_next: Callable) -> Response:
    """Log all incoming requests and outgoing responses.

    Args:
        request: Incoming request
        call_next: Next middleware/handler

    Returns:
        Response from handler
    """
    start_time = time.time()

    # Log request
    logger.info(
        f"Incoming request",
        extra={
            "extra_data": {
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
            }
        },
    )

    # Process request
    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info(
        f"Request completed",
        extra={
            "extra_data": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 3),
            }
        },
    )

    return response
