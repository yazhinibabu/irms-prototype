"""
Static code analysis module
"""
import ast
from typing import Dict, List, Any
from radon.complexity import cc_visit
from radon.metrics import h_visit, mi_visit
from utils.ast_helper import (
    get_function_info,
    get_class_info,
    get_imports,
    count_lines_of_code
)


class CodeAnalyzer:
    """Performs static analysis on Python source code."""
    
    def __init__(self):
        self.analysis_results: Dict[str, Dict] = {}
    
    def analyze_file(self, filename: str, source_code: str, tree: ast.Module) -> Dict[str, Any]:
        """
        Perform comprehensive static analysis on a Python file.
        
        Args:
            filename: Name of the file
            source_code: Source code string
            tree: AST of the file
            
        Returns:
            Dictionary containing analysis results
        """
        result = {
            'filename': filename,
            'metrics': self._calculate_metrics(source_code),
            'complexity': self._analyze_complexity(source_code),
            'structure': self._analyze_structure(tree),
            'issues': self._detect_issues(tree, source_code)
        }
        
        self.analysis_results[filename] = result
        return result
    
    def _calculate_metrics(self, source_code: str) -> Dict:
        """Calculate code metrics."""
        line_counts = count_lines_of_code(source_code)
        
        # Maintainability Index
        try:
            mi_score = mi_visit(source_code, multi=True)
            mi_value = mi_score if isinstance(mi_score, (int, float)) else 0
        except:
            mi_value = 0
        
        return {
            'lines': line_counts,
            'maintainability_index': round(mi_value, 2)
        }
    
    def _analyze_complexity(self, source_code: str) -> Dict:
        """Analyze cyclomatic complexity."""
        try:
            complexity_results = cc_visit(source_code)
            
            complexities = []
            for item in complexity_results:
                complexities.append({
                    'name': item.name,
                    'complexity': item.complexity,
                    'lineno': item.lineno,
                    'rank': self._get_complexity_rank(item.complexity)
                })
            
            avg_complexity = (
                sum(c['complexity'] for c in complexities) / len(complexities)
                if complexities else 0
            )
            
            return {
                'average': round(avg_complexity, 2),
                'functions': complexities,
                'high_complexity_count': sum(1 for c in complexities if c['complexity'] > 10)
            }
        except:
            return {
                'average': 0,
                'functions': [],
                'high_complexity_count': 0
            }
    
    def _analyze_structure(self, tree: ast.Module) -> Dict:
        """Analyze code structure."""
        return {
            'functions': get_function_info(tree),
            'classes': get_class_info(tree),
            'imports': get_imports(tree)
        }
    
    def _detect_issues(self, tree: ast.Module, source_code: str) -> List[Dict]:
        """Detect potential code issues."""
        issues = []
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append({
                        'type': 'missing_docstring',
                        'severity': 'low',
                        'line': node.lineno,
                        'message': f"{node.__class__.__name__} '{node.name}' missing docstring"
                    })
        
        # Check for bare excepts
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append({
                        'type': 'bare_except',
                        'severity': 'medium',
                        'line': node.lineno,
                        'message': 'Bare except clause detected - should catch specific exceptions'
                    })
        
        # Check for print statements (should use logging)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    issues.append({
                        'type': 'print_statement',
                        'severity': 'low',
                        'line': node.lineno,
                        'message': 'Consider using logging instead of print statements'
                    })
        
        # Check for TODO/FIXME comments
        for i, line in enumerate(source_code.split('\n'), 1):
            if 'TODO' in line or 'FIXME' in line:
                issues.append({
                    'type': 'todo_comment',
                    'severity': 'info',
                    'line': i,
                    'message': f'TODO/FIXME comment: {line.strip()}'
                })
        
        return issues
    
    def _get_complexity_rank(self, complexity: int) -> str:
        """Get complexity rank label."""
        if complexity <= 5:
            return 'A (simple)'
        elif complexity <= 10:
            return 'B (moderate)'
        elif complexity <= 20:
            return 'C (complex)'
        elif complexity <= 30:
            return 'D (very complex)'
        else:
            return 'F (extremely complex)'
    
    def get_analysis_summary(self) -> Dict:
        """Get summary of all analyzed files."""
        if not self.analysis_results:
            return {}
        
        total_issues = sum(
            len(result['issues'])
            for result in self.analysis_results.values()
        )
        
        avg_complexity = sum(
            result['complexity']['average']
            for result in self.analysis_results.values()
        ) / len(self.analysis_results)
        
        return {
            'files_analyzed': len(self.analysis_results),
            'total_issues': total_issues,
            'average_complexity': round(avg_complexity, 2),
            'files': list(self.analysis_results.keys())
        }
