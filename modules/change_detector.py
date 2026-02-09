"""
Change detection and tracking module
Enhanced with language-agnostic text diff support
"""
import difflib
from typing import Dict, List, Tuple


class ChangeDetector:
    """Detects and analyzes changes between original and modified code."""
    
    def __init__(self):
        self.changes: Dict[str, Dict] = {}
    
    def detect_changes(
        self,
        filename: str,
        original_code: str,
        modified_code: str
    ) -> Dict:
        """
        Backward-compatible wrapper for AST-based Python diff.
        Uses detect_text_diff internally.
        
        Args:
            filename: Name of the file
            original_code: Original source code
            modified_code: Modified source code
            
        Returns:
            Dictionary containing change analysis
        """
        return self.detect_text_diff(filename, original_code, modified_code)
    
    def detect_text_diff(
        self,
        filename: str,
        original_code: str,
        modified_code: str
    ) -> Dict:
        """
        Language-agnostic text-based diff detection.
        
        Args:
            filename: Name of the file
            original_code: Original source code
            modified_code: Modified source code
            
        Returns:
            Dictionary containing change analysis
        """
        # Generate unified diff
        diff = list(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            modified_code.splitlines(keepends=True),
            fromfile=f"{filename} (original)",
            tofile=f"{filename} (modified)",
            lineterm=''
        ))
        
        # Analyze changes
        analysis = {
            'filename': filename,
            'has_changes': original_code != modified_code,
            'diff': diff,
            'statistics': self._calculate_diff_stats(original_code, modified_code),
            'change_summary': self._summarize_changes(diff)
        }
        
        self.changes[filename] = analysis
        return analysis
    
    def _calculate_diff_stats(self, original: str, modified: str) -> Dict:
        """Calculate statistics about the changes."""
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()
        
        # Use SequenceMatcher for detailed comparison
        matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)
        
        additions = 0
        deletions = 0
        modifications = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                additions += (j2 - j1)
            elif tag == 'delete':
                deletions += (i2 - i1)
            elif tag == 'replace':
                modifications += max(i2 - i1, j2 - j1)
        
        return {
            'original_lines': len(original_lines),
            'modified_lines': len(modified_lines),
            'lines_added': additions,
            'lines_deleted': deletions,
            'lines_modified': modifications,
            'total_changes': additions + deletions + modifications
        }
    
    def _summarize_changes(self, diff: List[str]) -> str:
        """Generate a human-readable summary of changes."""
        if not diff:
            return "No changes detected"
        
        added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        summary = f"Modified {len(diff)} diff lines: "
        summary += f"+{added_lines} additions, -{removed_lines} deletions"
        
        return summary
    
    def get_diff_html(self, filename: str) -> str:
        """Generate HTML representation of diff for better visualization."""
        if filename not in self.changes:
            return "<p>No changes available</p>"
        
        diff_lines = self.changes[filename]['diff']
        html = ['<div class="diff-container" style="font-family: monospace; background: #f5f5f5; padding: 10px;">']
        
        for line in diff_lines:
            if line.startswith('+++') or line.startswith('---'):
                html.append(f'<div style="color: #666; font-weight: bold;">{line}</div>')
            elif line.startswith('+'):
                html.append(f'<div style="background: #d4ffd4; color: #006600;">{line}</div>')
            elif line.startswith('-'):
                html.append(f'<div style="background: #ffd4d4; color: #660000;">{line}</div>')
            elif line.startswith('@@'):
                html.append(f'<div style="background: #e0e0e0; color: #000080;">{line}</div>')
            else:
                html.append(f'<div>{line}</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def get_all_changes(self) -> Dict[str, Dict]:
        """Get all detected changes."""
        return self.changes.copy()
    
    def format_diff_for_report(self, filename: str, max_lines: int = 50) -> str:
        """Format diff for text report."""
        if filename not in self.changes:
            return "No changes detected"
        
        diff_lines = self.changes[filename]['diff']
        
        if not diff_lines:
            return "No changes detected"
        
        # Limit output for readability
        output_lines = diff_lines[:max_lines]
        result = '\n'.join(output_lines)
        
        if len(diff_lines) > max_lines:
            result += f"\n\n... ({len(diff_lines) - max_lines} more lines omitted)"
        
        return result