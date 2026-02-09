"""
Python language handler for IRMS
"""
from modules.languages.base import BaseLanguageHandler
from modules.code_analyzer import CodeAnalyzer
from modules.change_detector import ChangeDetector
import ast
from typing import Any, Dict


class PythonHandler(BaseLanguageHandler):
    """Handler for Python language files."""

    def parse(self, source_code: str) -> ast.Module:
        """
        Parse Python source code into AST.
        
        Args:
            source_code: Python source code string
            
        Returns:
            AST Module
        """
        return ast.parse(source_code)

    def analyze(self, tree: Any, source_code: str) -> Dict:
        """
        Analyze Python code using static analysis.
        
        Args:
            tree: AST tree
            source_code: Source code string
            
        Returns:
            Analysis results dictionary
        """
        analyzer = CodeAnalyzer()
        return analyzer.analyze_file(
            filename="<python>",
            source_code=source_code,
            tree=tree
        )

    def diff(self, original: str, modified: str) -> Dict:
        """
        Detect changes between original and modified Python code.
        
        Args:
            original: Original code
            modified: Modified code
            
        Returns:
            Diff analysis dictionary
        """
        detector = ChangeDetector()
        return detector.detect_text_diff("<python>", original, modified)

    def ai_prompt_context(self) -> str:
        """
        Get AI prompt context for Python code.
        
        Returns:
            Context string for AI prompts
        """
        return "The following code is written in Python."