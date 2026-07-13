from typing import Any


def success_response(message: str = "Operation Successful", data: Any = None):
    """Create the standard success payload expected by the Android app."""
    return {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
    }


def error_response(message: str, status_code: int = 400):
    """Create the standard error payload expected by the Android app."""
    return {
        "success": False,
        "message": message,
    }, status_code
