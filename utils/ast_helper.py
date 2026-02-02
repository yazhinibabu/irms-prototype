"""
AST manipulation and analysis utilities
"""
import ast
from typing import Dict, List, Any


def parse_python_file(file_path: str) -> ast.Module:
    """
    Parse a Python file into an AST.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        AST Module node
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    return ast.parse(source_code, filename=file_path)


def get_function_info(tree: ast.Module) -> List[Dict[str, Any]]:
    """
    Extract information about all functions in the AST.
    
    Args:
        tree: AST Module
        
    Returns:
        List of function metadata dictionaries
    """
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'lineno': node.lineno,
                'args': [arg.arg for arg in node.args.args],
                'returns': ast.unparse(node.returns) if node.returns else None,
                'docstring': ast.get_docstring(node),
                'decorators': [ast.unparse(dec) for dec in node.decorator_list]
            })
    
    return functions


def get_class_info(tree: ast.Module) -> List[Dict[str, Any]]:
    """
    Extract information about all classes in the AST.
    
    Args:
        tree: AST Module
        
    Returns:
        List of class metadata dictionaries
    """
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            classes.append({
                'name': node.name,
                'lineno': node.lineno,
                'bases': [ast.unparse(base) for base in node.bases],
                'methods': methods,
                'docstring': ast.get_docstring(node)
            })
    
    return classes


def get_imports(tree: ast.Module) -> List[str]:
    """
    Extract all import statements.
    
    Args:
        tree: AST Module
        
    Returns:
        List of import strings
    """
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"from {module} import {alias.name}")
    
    return imports


def count_lines_of_code(source_code: str) -> Dict[str, int]:
    """
    Count different types of lines in source code.
    
    Args:
        source_code: Python source code string
        
    Returns:
        Dictionary with line counts
    """
    lines = source_code.split('\n')
    
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
    code_lines = total_lines - blank_lines - comment_lines
    
    return {
        'total': total_lines,
        'code': code_lines,
        'blank': blank_lines,
        'comments': comment_lines
    }
