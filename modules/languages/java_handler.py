"""
Java language handler for IRMS
"""
from modules.languages.base import BaseLanguageHandler
from modules.change_detector import ChangeDetector
from typing import Any, Dict
import re


class JavaHandler(BaseLanguageHandler):
    """Handler for Java language files."""

    def parse(self, source_code: str) -> Dict[str, Any]:
        """
        Parse Java source code (text-based, no AST).
        
        Args:
            source_code: Java source code string
            
        Returns:
            Dictionary with parsed information
        """
        parsed = {
            'source': source_code,
            'classes': self._extract_classes(source_code),
            'methods': self._extract_methods(source_code),
            'imports': self._extract_imports(source_code),
            'package': self._extract_package(source_code)
        }
        return parsed

    def analyze(self, tree: Any, source_code: str) -> Dict:
        """
        Analyze Java code (basic text-based analysis).
        
        Args:
            tree: Parsed data from parse()
            source_code: Source code string
            
        Returns:
            Analysis results dictionary
        """
        lines = source_code.split('\n')
        
        # Count various constructs
        issues = []
        complexity = self._estimate_complexity(source_code)
        
        # Check for common issues
        issues.extend(self._check_naming_conventions(source_code))
        issues.extend(self._check_common_issues(source_code))
        
        analysis = {
            'complexity': {
                'average': complexity,
                'max': complexity,
                'min': complexity
            },
            'metrics': {
                'maintainability_index': max(0, 100 - complexity * 2),
                'loc': len(lines),
                'methods': len(tree.get('methods', [])),
                'classes': len(tree.get('classes', []))
            },
            'issues': issues,
            'functions': tree.get('methods', []),
            'classes': tree.get('classes', [])
        }
        
        return analysis

    def diff(self, original: str, modified: str) -> Dict:
        """
        Detect changes between original and modified Java code.
        
        Args:
            original: Original code
            modified: Modified code
            
        Returns:
            Diff analysis dictionary
        """
        detector = ChangeDetector()
        return detector.detect_text_diff("<java>", original, modified)

    def ai_prompt_context(self) -> str:
        """
        Get AI prompt context for Java code.
        
        Returns:
            Context string for AI prompts
        """
        return """The following code is written in Java.
Follow Java naming conventions (CamelCase for classes, camelCase for methods).
Use proper access modifiers (public, private, protected).
Follow Java best practices and design patterns."""

    # Helper methods for parsing
    
    def _extract_classes(self, source_code: str) -> list:
        """Extract class names from Java code."""
        pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)'
        matches = re.finditer(pattern, source_code)
        return [match.group(1) for match in matches]
    
    def _extract_methods(self, source_code: str) -> list:
        """Extract method signatures from Java code."""
        pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(?:\w+)\s+(\w+)\s*\([^)]*\)'
        matches = re.finditer(pattern, source_code)
        methods = []
        for match in matches:
            method_name = match.group(1)
            # Filter out common keywords that aren't methods
            if method_name not in ['if', 'for', 'while', 'switch', 'catch', 'class', 'interface']:
                methods.append(method_name)
        return methods
    
    def _extract_imports(self, source_code: str) -> list:
        """Extract import statements."""
        pattern = r'import\s+([\w.]+);'
        matches = re.finditer(pattern, source_code)
        return [match.group(1) for match in matches]
    
    def _extract_package(self, source_code: str) -> str:
        """Extract package name."""
        pattern = r'package\s+([\w.]+);'
        match = re.search(pattern, source_code)
        return match.group(1) if match else ''
    
    def _estimate_complexity(self, source_code: str) -> float:
        """Estimate cyclomatic complexity (simplified)."""
        # Count decision points
        complexity = 1  # Base complexity
        
        # Count control flow statements
        complexity += source_code.count('if ')
        complexity += source_code.count('else ')
        complexity += source_code.count('for ')
        complexity += source_code.count('while ')
        complexity += source_code.count('case ')
        complexity += source_code.count('catch ')
        complexity += source_code.count('&&')
        complexity += source_code.count('||')
        
        # Normalize by number of methods
        methods = self._extract_methods(source_code)
        if methods:
            complexity = complexity / len(methods)
        
        return round(complexity, 2)
    
    def _check_naming_conventions(self, source_code: str) -> list:
        """Check Java naming conventions."""
        issues = []
        lines = source_code.split('\n')
        
        # Check class names (should start with uppercase)
        class_pattern = r'class\s+([a-z]\w*)'
        for i, line in enumerate(lines, 1):
            match = re.search(class_pattern, line)
            if match:
                issues.append({
                    'line': i,
                    'message': f"Class name '{match.group(1)}' should start with uppercase letter",
                    'severity': 'medium',
                    'type': 'naming'
                })
        
        # Check method names (should start with lowercase)
        method_pattern = r'(?:public|private|protected)\s+\w+\s+([A-Z]\w*)\s*\('
        for i, line in enumerate(lines, 1):
            match = re.search(method_pattern, line)
            if match:
                issues.append({
                    'line': i,
                    'message': f"Method name '{match.group(1)}' should start with lowercase letter",
                    'severity': 'low',
                    'type': 'naming'
                })
        
        return issues
    
    def _check_common_issues(self, source_code: str) -> list:
        """Check for common Java issues."""
        issues = []
        lines = source_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for System.out.println (should use logger)
            if 'System.out.println' in line:
                issues.append({
                    'line': i,
                    'message': 'Consider using a logger instead of System.out.println',
                    'severity': 'low',
                    'type': 'best_practice'
                })
            
            # Check for empty catch blocks
            if 'catch' in line and i + 1 < len(lines):
                next_line = lines[i].strip()
                if next_line == '}' or next_line == '':
                    issues.append({
                        'line': i,
                        'message': 'Empty catch block - consider logging the exception',
                        'severity': 'high',
                        'type': 'error_handling'
                    })
        
        return issues