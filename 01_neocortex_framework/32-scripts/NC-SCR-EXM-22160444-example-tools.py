# @UBL @UBL @SCR-EXM | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
Example Tools Implementation
---
"""

"""---
Example Tools Implementation
---
"""

"""
Example Tools Implementation
Contains handler functions for the example tools
"""

import os
import time
from datetime import datetime
from typing import Dict, Any

def echo_function(text: str, repeat: int = 1, uppercase: bool = False) -> Dict[str, Any]:
    """
    Echo tool handler function
    
    Args:
        text: Text to echo
        repeat: Number of times to repeat
        uppercase: Convert to uppercase
    
    Returns:
        Dictionary with echoed text
    """
    if uppercase:
        text = text.upper()
    
    result = "\n".join([text] * repeat)
    
    return {
        "original_text": text,
        "repeated": repeat,
        "uppercase": uppercase,
        "result": result,
        "timestamp": datetime.now().isoformat(),
        "characters": len(text) * repeat
    }

def calculate(operation: str, a: float, b: float, precision: int = 2) -> Dict[str, Any]:
    """
    Calculator tool handler function
    
    Args:
        operation: Arithmetic operation
        a: First number
        b: Second number
        precision: Decimal precision
    
    Returns:
        Dictionary with calculation result
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else float('inf')
    }
    
    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}. Valid options: {list(operations.keys())}")
    
    try:
        result = operations[operation](a, b)
        
        # Format with precision
        if isinstance(result, float):
            result = round(result, precision)
        
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
            "precision": precision,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    
    except ZeroDivisionError:
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": "infinity",
            "error": "Division by zero",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }
    
    except Exception as e:
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

def get_file_info(file_path: str, include_content: bool = False, max_content_size: int = 10240) -> Dict[str, Any]:
    """
    File info tool handler function
    
    Args:
        file_path: Path to the file
        include_content: Include file content
        max_content_size: Maximum content size to read
    
    Returns:
        Dictionary with file information
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "file_path": file_path,
                "exists": False,
                "error": "File not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get file stats
        stat = os.stat(file_path)
        
        result = {
            "file_path": file_path,
            "exists": True,
            "size_bytes": stat.st_size,
            "size_human": _format_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "is_file": os.path.isfile(file_path),
            "is_directory": os.path.isdir(file_path),
            "timestamp": datetime.now().isoformat()
        }
        
        # Include content if requested
        if include_content and os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(max_content_size)
                    result["content_preview"] = content
                    result["content_truncated"] = len(content) == max_content_size
            except Exception as e:
                result["content_error"] = str(e)
        
        return result
    
    except Exception as e:
        return {
            "file_path": file_path,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

# Additional example tools

def system_info() -> Dict[str, Any]:
    """Get system information"""
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "processor": platform.processor(),
        "system": platform.system(),
        "release": platform.release(),
        "timestamp": datetime.now().isoformat(),
        "working_directory": os.getcwd()
    }

def delay_execution(seconds: int, message: str = "Done") -> Dict[str, Any]:
    """Delay execution for specified seconds"""
    start_time = time.time()
    time.sleep(seconds)
    end_time = time.time()
    
    return {
        "message": message,
        "requested_delay": seconds,
        "actual_delay": end_time - start_time,
        "start_time": datetime.fromtimestamp(start_time).isoformat(),
        "end_time": datetime.fromtimestamp(end_time).isoformat(),
        "timestamp": datetime.now().isoformat()
    }

def string_operations(text: str, operation: str = "reverse") -> Dict[str, Any]:
    """Perform string operations"""
    operations = {
        "reverse": lambda s: s[::-1],
        "uppercase": lambda s: s.upper(),
        "lowercase": lambda s: s.lower(),
        "title": lambda s: s.title(),
        "length": lambda s: len(s),
        "words": lambda s: len(s.split()),
        "chars": lambda s: len(s.replace(" ", ""))
    }
    
    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}")
    
    result = operations[operation](text)
    
    return {
        "original": text,
        "operation": operation,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

# Test function to verify the module works
def test_all_tools():
    """Test all example tools"""
    print("Testing example tools...")
    
    # Test echo function
    echo_result = echo_function("Hello, World!", repeat=2, uppercase=True)
    print(f"Echo test: {echo_result}")
    
    # Test calculator
    calc_result = calculate("add", 10, 5)
    print(f"Calculator test: {calc_result}")
    
    # Test file info (current file)
    file_result = get_file_info(__file__, include_content=True, max_content_size=500)
    print(f"File info test: Keys: {list(file_result.keys())}")
    
    # Test system info
    sys_result = system_info()
    print(f"System info test: Platform: {sys_result['platform']}")
    
    # Test string operations
    str_result = string_operations("hello world", "uppercase")
    print(f"String operations test: {str_result}")
    
    print("All tests completed!")

if __name__ == "__main__":
    test_all_tools()
