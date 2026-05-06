import logging
from functools import wraps
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

def mcp_error(message: str, suggestion: Optional[str] = None, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Format a standard MCP tool error response according to Spec §7.2 and SEP-1303.
    """
    error_msg = f"Error: {message}"
    if suggestion:
        error_msg += f" Suggestion: {suggestion}"
    if context:
        error_msg += f" Context: {context}"
    
    return {
        "content": [{"type": "text", "text": error_msg}],
        "isError": True
    }

def mcp_success(data: Any) -> Dict[str, Any]:
    """
    Format a standard MCP tool success response.
    """
    if isinstance(data, str):
        text = data
    else:
        import json
        try:
            text = json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            text = str(data)
            
    return {
        "content": [{"type": "text", "text": text}],
        "isError": False
    }


def mcp_response(fn):
    """Decorator: auto-wraps tool return values into mcp_success/mcp_error format.
    
    If the function returns a dict with 'success': False, wraps as mcp_error.
    Otherwise wraps as mcp_success.
    Returns the raw result unchanged if it's already an MCP content format.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        if not isinstance(result, dict):
            return mcp_success(result)
        if "content" in result and "isError" in result:
            return result
        if result.get("success") is False:
            return mcp_error(
                result.get("error", result.get("message", "unknown error")),
                suggestion=result.get("suggestion"),
                context=result.get("context"),
            )
        return mcp_success(result)
    return wrapper
