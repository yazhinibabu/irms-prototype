"""
AST (Abstract Syntax Tree) parsing utilities
"""
import ast
from typing import Dict, List, Optional, Any


def parse_python_file(file_path: str) -> Optional[ast.Module]:
    """
    Parse a Python file into an AST.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        AST Module or None if parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        return ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        print(f"⚠ Syntax error in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"⚠ Error parsing {file_path}: {e}")
        return None


def get_function_info(tree: ast.Module) -> List[Dict[str, Any]]:
    """
    Extract function information from AST.
    
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
                'docstring': ast.get_docstring(node),
                'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
            })
    
    return functions


def get_class_info(tree: ast.Module) -> List[Dict[str, Any]]:
    """
    Extract class information from AST.
    
    Args:
        tree: AST Module
        
    Returns:
        List of class metadata dictionaries
    """
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in node.body 
                if isinstance(n, ast.FunctionDef)
            ]
            
            classes.append({
                'name': node.name,
                'lineno': node.lineno,
                'methods': methods,
                'docstring': ast.get_docstring(node),
                'bases': [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases]
            })
    
    return classes


def get_imports(tree: ast.Module) -> List[str]:
    """
    Extract import statements from AST.
    
    Args:
        tree: AST Module
        
    Returns:
        List of import names
    """
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
    
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
    
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comments = sum(1 for line in lines if line.strip().startswith('#'))
    code = total - blank - comments
    
    return {
        'total': total,
        'code': code,
        'comments': comments,
        'blank': blank
    }