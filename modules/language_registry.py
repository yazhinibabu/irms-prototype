"""
Language handler registry for IRMS
Maps file extensions to appropriate language handlers
"""
from typing import Dict, Optional
from modules.languages.base import BaseLanguageHandler
from modules.languages.python_handler import PythonHandler
from modules.languages.java_handler import JavaHandler
from modules.languages.cpp_handler import CppHandler
from modules.languages.javascript_handler import JavaScriptHandler


# Register all language handlers
LANGUAGE_HANDLERS: Dict[str, BaseLanguageHandler] = {
    # Python
    ".py": PythonHandler(),
    
    # Java
    ".java": JavaHandler(),
    
    # C/C++
    ".c": CppHandler(),
    ".cpp": CppHandler(),
    ".cc": CppHandler(),
    ".cxx": CppHandler(),
    ".h": CppHandler(),
    ".hpp": CppHandler(),
    ".hxx": CppHandler(),
    
    # JavaScript/TypeScript
    ".js": JavaScriptHandler(),
    ".jsx": JavaScriptHandler(),
    ".ts": JavaScriptHandler(),
    ".tsx": JavaScriptHandler(),
    ".mjs": JavaScriptHandler(),
    ".cjs": JavaScriptHandler(),
}


def get_handler_for_file(filename: str) -> Optional[BaseLanguageHandler]:
    """
    Get the appropriate language handler for a given filename.
    
    Args:
        filename: Name of the file (e.g., "main.py", "App.java", "index.js")
        
    Returns:
        Language handler instance or None if no handler found
    """
    for ext, handler in LANGUAGE_HANDLERS.items():
        if filename.endswith(ext):
            return handler
    return None


def get_supported_extensions() -> list:
    """
    Get list of all supported file extensions.
    
    Returns:
        List of file extensions (e.g., [".py", ".java", ".js"])
    """
    return list(LANGUAGE_HANDLERS.keys())


def is_supported_file(filename: str) -> bool:
    """
    Check if a file is supported by any registered handler.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if supported, False otherwise
    """
    return get_handler_for_file(filename) is not None


def get_language_name(filename: str) -> str:
    """
    Get the language name for a file.
    
    Args:
        filename: Name of the file
        
    Returns:
        Language name (e.g., "Python", "JavaScript") or "Unknown"
    """
    if filename.endswith('.py'):
        return "Python"
    elif filename.endswith('.java'):
        return "Java"
    elif filename.endswith(('.c', '.h')):
        return "C"
    elif filename.endswith(('.cpp', '.cc', '.cxx', '.hpp', '.hxx')):
        return "C++"
    elif filename.endswith(('.js', '.mjs', '.cjs')):
        return "JavaScript"
    elif filename.endswith('.jsx'):
        return "JavaScript (React)"
    elif filename.endswith('.ts'):
        return "TypeScript"
    elif filename.endswith('.tsx'):
        return "TypeScript (React)"
    else:
        return "Unknown"