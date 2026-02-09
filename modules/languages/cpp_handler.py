"""
C/C++ language handler for IRMS
"""
from modules.languages.base import BaseLanguageHandler
from modules.change_detector import ChangeDetector
from typing import Any, Dict
import re


class CppHandler(BaseLanguageHandler):
    """Handler for C and C++ language files."""

    def parse(self, source_code: str) -> Dict[str, Any]:
        """
        Parse C/C++ source code (text-based, no AST).
        
        Args:
            source_code: C/C++ source code string
            
        Returns:
            Dictionary with parsed information
        """
        parsed = {
            'source': source_code,
            'functions': self._extract_functions(source_code),
            'classes': self._extract_classes(source_code),
            'includes': self._extract_includes(source_code),
            'namespaces': self._extract_namespaces(source_code),
            'is_cpp': self._is_cpp_code(source_code)
        }
        return parsed

    def analyze(self, tree: Any, source_code: str) -> Dict:
        """
        Analyze C/C++ code (basic text-based analysis).
        
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
        issues.extend(self._check_memory_issues(source_code))
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
        Detect changes between original and modified C/C++ code.
        
        Args:
            original: Original code
            modified: Modified code
            
        Returns:
            Diff analysis dictionary
        """
        detector = ChangeDetector()
        return detector.detect_text_diff("<c/c++>", original, modified)

    def ai_prompt_context(self) -> str:
        """
        Get AI prompt context for C/C++ code.
        
        Returns:
            Context string for AI prompts
        """
        return """The following code is written in C/C++.
Pay attention to memory management (malloc/free, new/delete).
Check for buffer overflows and pointer safety.
Use RAII principles for C++ code.
Follow modern C++ best practices (prefer smart pointers, avoid raw pointers when possible)."""

    # Helper methods for parsing
    
    def _is_cpp_code(self, source_code: str) -> bool:
        """Detect if code is C++ (vs plain C)."""
        cpp_indicators = [
            'class ', 'namespace ', 'template', 'std::', 
            'cout', 'cin', 'new ', 'delete ', 'try ', 'catch'
        ]
        return any(indicator in source_code for indicator in cpp_indicators)
    
    def _extract_functions(self, source_code: str) -> list:
        """Extract function definitions from C/C++ code."""
        # Pattern for function definitions
        pattern = r'(?:[\w\s\*&]+)\s+(\w+)\s*\([^)]*\)\s*(?:const)?\s*{'
        matches = re.finditer(pattern, source_code)
        functions = []
        for match in matches:
            func_name = match.group(1)
            # Filter out common keywords
            if func_name not in ['if', 'for', 'while', 'switch', 'catch']:
                functions.append(func_name)
        return functions
    
    def _extract_classes(self, source_code: str) -> list:
        """Extract class names from C++ code."""
        pattern = r'class\s+(\w+)'
        matches = re.finditer(pattern, source_code)
        return [match.group(1) for match in matches]
    
    def _extract_includes(self, source_code: str) -> list:
        """Extract include statements."""
        pattern = r'#include\s*[<"]([^>"]+)[>"]'
        matches = re.finditer(pattern, source_code)
        return [match.group(1) for match in matches]
    
    def _extract_namespaces(self, source_code: str) -> list:
        """Extract namespace declarations."""
        pattern = r'namespace\s+(\w+)'
        matches = re.finditer(pattern, source_code)
        return [match.group(1) for match in matches]
    
    def _estimate_complexity(self, source_code: str) -> float:
        """Estimate cyclomatic complexity (simplified)."""
        complexity = 1  # Base complexity
        
        # Count control flow statements
        complexity += source_code.count('if(')
        complexity += source_code.count('if (')
        complexity += source_code.count('else')
        complexity += source_code.count('for(')
        complexity += source_code.count('for (')
        complexity += source_code.count('while(')
        complexity += source_code.count('while (')
        complexity += source_code.count('case ')
        complexity += source_code.count('&&')
        complexity += source_code.count('||')
        complexity += source_code.count('?')  # Ternary operator
        
        # Normalize by number of functions
        functions = self._extract_functions(source_code)
        if functions:
            complexity = complexity / len(functions)
        
        return round(complexity, 2)
    
    def _check_memory_issues(self, source_code: str) -> list:
        """Check for potential memory issues."""
        issues = []
        lines = source_code.split('\n')
        
        malloc_count = 0
        free_count = 0
        new_count = 0
        delete_count = 0
        
        for i, line in enumerate(lines, 1):
            # Check malloc/free balance
            if 'malloc(' in line or 'calloc(' in line:
                malloc_count += 1
                issues.append({
                    'line': i,
                    'message': 'Manual memory allocation - ensure corresponding free() exists',
                    'severity': 'medium',
                    'type': 'memory'
                })
            
            if 'free(' in line:
                free_count += 1
            
            # Check new/delete balance
            if re.search(r'\bnew\s+', line):
                new_count += 1
                issues.append({
                    'line': i,
                    'message': 'Raw pointer allocation - consider using smart pointers (unique_ptr/shared_ptr)',
                    'severity': 'medium',
                    'type': 'memory'
                })
            
            if 'delete ' in line:
                delete_count += 1
            
            # Check for potential buffer overflow
            if 'strcpy(' in line or 'strcat(' in line:
                issues.append({
                    'line': i,
                    'message': 'Unsafe string function - use strncpy or strcat_s instead',
                    'severity': 'high',
                    'type': 'security'
                })
            
            # Check for gets() (extremely dangerous)
            if 'gets(' in line:
                issues.append({
                    'line': i,
                    'message': 'gets() is dangerous and deprecated - use fgets() instead',
                    'severity': 'critical',
                    'type': 'security'
                })
            
            # Check for NULL pointer usage without check
            if re.search(r'\*\s*\w+\s*[=;]', line) and 'if' not in line:
                if i > 1 and 'if' not in lines[i-2]:
                    issues.append({
                        'line': i,
                        'message': 'Potential NULL pointer dereference - add NULL check',
                        'severity': 'high',
                        'type': 'safety'
                    })
        
        # Check for memory leak patterns
        if malloc_count > free_count:
            issues.append({
                'line': 0,
                'message': f'Potential memory leak - {malloc_count} malloc/calloc but only {free_count} free',
                'severity': 'high',
                'type': 'memory'
            })
        
        if new_count > delete_count:
            issues.append({
                'line': 0,
                'message': f'Potential memory leak - {new_count} new but only {delete_count} delete',
                'severity': 'high',
                'type': 'memory'
            })
        
        return issues
    
    def _check_common_issues(self, source_code: str) -> list:
        """Check for common C/C++ issues."""
        issues = []
        lines = source_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for magic numbers
            if re.search(r'\b\d{3,}\b', line) and 'define' not in line:
                issues.append({
                    'line': i,
                    'message': 'Magic number detected - consider using named constant',
                    'severity': 'low',
                    'type': 'maintainability'
                })
            
            # Check for single character variable names (except i, j, k in loops)
            if re.search(r'\b[a-hln-z]\s*=', line) and 'for' not in line:
                issues.append({
                    'line': i,
                    'message': 'Single character variable name - use descriptive names',
                    'severity': 'low',
                    'type': 'readability'
                })
            
            # Check for using namespace std in headers
            if 'using namespace std' in line:
                issues.append({
                    'line': i,
                    'message': 'Avoid "using namespace std" in headers - causes namespace pollution',
                    'severity': 'medium',
                    'type': 'best_practice'
                })
            
            # Check for C-style casts in C++ code
            if self._is_cpp_code(source_code):
                if re.search(r'\([A-Za-z_]\w*\s*\*?\s*\)', line):
                    issues.append({
                        'line': i,
                        'message': 'C-style cast detected - use static_cast/dynamic_cast/const_cast',
                        'severity': 'low',
                        'type': 'modern_cpp'
                    })
        
        return issues