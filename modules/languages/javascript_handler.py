"""
JavaScript language handler for IRMS
"""
from modules.languages.base import BaseLanguageHandler
from modules.change_detector import ChangeDetector
from typing import Any, Dict
import re


class JavaScriptHandler(BaseLanguageHandler):
    """Handler for JavaScript and TypeScript files."""

    def parse(self, source_code: str) -> Dict[str, Any]:
        """
        Parse JavaScript source code (text-based, no AST).
        
        Args:
            source_code: JavaScript source code string
            
        Returns:
            Dictionary with parsed information
        """
        parsed = {
            'source': source_code,
            'functions': self._extract_functions(source_code),
            'classes': self._extract_classes(source_code),
            'imports': self._extract_imports(source_code),
            'exports': self._extract_exports(source_code),
            'is_typescript': self._is_typescript(source_code),
            'is_react': self._is_react(source_code)
        }
        return parsed

    def analyze(self, tree: Any, source_code: str) -> Dict:
        """
        Analyze JavaScript code (basic text-based analysis).
        
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
        issues.extend(self._check_common_issues(source_code))
        issues.extend(self._check_best_practices(source_code))
        
        analysis = {
            'complexity': {
                'average': complexity,
                'max': complexity,
                'min': complexity
            },
            'metrics': {
                'maintainability_index': max(0, 100 - complexity * 2),
                'loc': len(lines),
                'functions': len(tree.get('functions', [])),
                'classes': len(tree.get('classes', []))
            },
            'issues': issues,
            'functions': tree.get('functions', []),
            'classes': tree.get('classes', [])
        }
        
        return analysis

    def diff(self, original: str, modified: str) -> Dict:
        """
        Detect changes between original and modified JavaScript code.
        
        Args:
            original: Original code
            modified: Modified code
            
        Returns:
            Diff analysis dictionary
        """
        detector = ChangeDetector()
        return detector.detect_text_diff("<javascript>", original, modified)

    def ai_prompt_context(self) -> str:
        """
        Get AI prompt context for JavaScript code.
        
        Returns:
            Context string for AI prompts
        """
        return """The following code is written in JavaScript (ES6+).
Follow modern JavaScript best practices:
- Use const/let instead of var
- Use arrow functions where appropriate
- Use async/await for promises
- Add proper error handling with try-catch
- Use template literals for string interpolation
- Follow ESLint recommended rules"""

    # Helper methods for parsing
    
    def _is_typescript(self, source_code: str) -> bool:
        """Detect if code is TypeScript."""
        ts_indicators = [
            'interface ', 'type ', ': string', ': number', ': boolean',
            '<T>', 'enum ', 'implements ', 'private ', 'public ', 'protected '
        ]
        return any(indicator in source_code for indicator in ts_indicators)
    
    def _is_react(self, source_code: str) -> bool:
        """Detect if code is React."""
        react_indicators = [
            'import React', 'from \'react\'', 'from "react"',
            'useState', 'useEffect', 'jsx', 'tsx', '<div', 'className='
        ]
        return any(indicator in source_code for indicator in react_indicators)
    
    def _extract_functions(self, source_code: str) -> list:
        """Extract function declarations from JavaScript code."""
        functions = []
        
        # Regular function declarations: function name()
        pattern1 = r'function\s+(\w+)\s*\('
        functions.extend(re.findall(pattern1, source_code))
        
        # Arrow functions: const name = () =>
        pattern2 = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=])\s*=>'
        functions.extend(re.findall(pattern2, source_code))
        
        # Method definitions: methodName()
        pattern3 = r'(\w+)\s*\([^)]*\)\s*\{'
        methods = re.findall(pattern3, source_code)
        # Filter out keywords
        keywords = ['if', 'for', 'while', 'switch', 'catch', 'function']
        functions.extend([m for m in methods if m not in keywords and m not in functions])
        
        return list(set(functions))  # Remove duplicates
    
    def _extract_classes(self, source_code: str) -> list:
        """Extract class names from JavaScript code."""
        pattern = r'class\s+(\w+)'
        matches = re.finditer(pattern, source_code)
        return [match.group(1) for match in matches]
    
    def _extract_imports(self, source_code: str) -> list:
        """Extract import statements."""
        imports = []
        
        # ES6 imports: import X from 'Y'
        pattern1 = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
        imports.extend(re.findall(pattern1, source_code))
        
        # Require statements: require('X')
        pattern2 = r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        imports.extend(re.findall(pattern2, source_code))
        
        return imports
    
    def _extract_exports(self, source_code: str) -> list:
        """Extract export statements."""
        exports = []
        
        # export default
        if 'export default' in source_code:
            exports.append('default')
        
        # export { X }
        pattern = r'export\s+\{([^}]+)\}'
        matches = re.findall(pattern, source_code)
        for match in matches:
            exports.extend([x.strip() for x in match.split(',')])
        
        # export const/let/var/function/class
        pattern2 = r'export\s+(?:const|let|var|function|class)\s+(\w+)'
        exports.extend(re.findall(pattern2, source_code))
        
        return exports
    
    def _estimate_complexity(self, source_code: str) -> float:
        """Estimate cyclomatic complexity (simplified)."""
        complexity = 1  # Base complexity
        
        # Count control flow statements
        complexity += source_code.count('if(')
        complexity += source_code.count('if (')
        complexity += source_code.count('else if')
        complexity += source_code.count('else ')
        complexity += source_code.count('for(')
        complexity += source_code.count('for (')
        complexity += source_code.count('while(')
        complexity += source_code.count('while (')
        complexity += source_code.count('case ')
        complexity += source_code.count('catch ')
        complexity += source_code.count('&&')
        complexity += source_code.count('||')
        complexity += source_code.count('?')  # Ternary operator
        
        # Normalize by number of functions
        functions = self._extract_functions(source_code)
        if functions:
            complexity = complexity / len(functions)
        
        return round(complexity, 2)
    
    def _check_common_issues(self, source_code: str) -> list:
        """Check for common JavaScript issues."""
        issues = []
        lines = source_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for var usage (should use let/const)
            if re.search(r'\bvar\s+\w+', line):
                issues.append({
                    'line': i,
                    'message': 'Use const or let instead of var',
                    'severity': 'medium',
                    'type': 'modern_js'
                })
            
            # Check for == instead of ===
            if '==' in line and '===' not in line and '!==' not in line:
                issues.append({
                    'line': i,
                    'message': 'Use === instead of == for comparison',
                    'severity': 'medium',
                    'type': 'best_practice'
                })
            
            # Check for console.log (should be removed in production)
            if 'console.log' in line:
                issues.append({
                    'line': i,
                    'message': 'Remove console.log statements before production',
                    'severity': 'low',
                    'type': 'cleanup'
                })
            
            # Check for eval() usage (dangerous)
            if 'eval(' in line:
                issues.append({
                    'line': i,
                    'message': 'Avoid using eval() - potential security risk',
                    'severity': 'critical',
                    'type': 'security'
                })
            
            # Check for empty catch blocks
            if 'catch' in line:
                # Look ahead for empty block
                if i < len(lines):
                    next_lines = ' '.join(lines[i:min(i+3, len(lines))]).strip()
                    if 'catch' in next_lines and '{}' in next_lines:
                        issues.append({
                            'line': i,
                            'message': 'Empty catch block - handle errors properly',
                            'severity': 'high',
                            'type': 'error_handling'
                        })
        
        return issues
    
    def _check_best_practices(self, source_code: str) -> list:
        """Check for JavaScript best practices."""
        issues = []
        lines = source_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for magic numbers
            magic_number = re.search(r'\b\d{3,}\b', line)
            if magic_number and 'const' not in line and 'let' not in line:
                issues.append({
                    'line': i,
                    'message': 'Magic number detected - use named constants',
                    'severity': 'low',
                    'type': 'maintainability'
                })
            
            # Check for single letter variable names (except i, j, k in loops)
            if 'for' not in line:
                single_var = re.search(r'\b(?:const|let|var)\s+([a-hln-z])\s*=', line)
                if single_var:
                    issues.append({
                        'line': i,
                        'message': f"Single letter variable '{single_var.group(1)}' - use descriptive names",
                        'severity': 'low',
                        'type': 'readability'
                    })
        
        return issues