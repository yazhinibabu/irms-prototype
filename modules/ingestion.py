"""
File ingestion and parsing module
Enhanced with project-level ingestion and .gitignore support
"""
from pathlib import Path
from typing import Dict, List, Optional, Set
import ast
import fnmatch
import os

# Import with proper type checking
try:
    from utils.pdf_parser import extract_text_from_pdf, extract_text_from_txt
    from utils.ast_helper import parse_python_file
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Fallback stubs with proper signatures
    def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
        """Fallback stub for PDF extraction."""
        return None
    
    def extract_text_from_txt(txt_path: Path) -> Optional[str]:
        """Fallback stub for text extraction."""
        return None
    
    def parse_python_file(file_path: str) -> Optional[ast.Module]:
        """Fallback stub for Python parsing."""
        return None


class FileIngestion:
    """Handles ingestion of Python source files and supporting documents."""
    
    def __init__(
        self, 
        code_dir: Path, 
        docs_dir: Optional[Path] = None,
        project_root: Optional[Path] = None,
        recursive: bool = False,
        ignore_patterns: Optional[List[str]] = None,
        max_file_size: int = 5 * 1024 * 1024  # 5MB default
    ):
        """
        Initialize the ingestion system.
        
        Args:
            code_dir: Directory containing Python source files
            docs_dir: Directory containing supporting documents (optional)
            project_root: Root directory for project-level ingestion (NEW)
            recursive: Enable recursive directory scanning (NEW)
            ignore_patterns: Patterns to ignore (like .gitignore) (NEW)
            max_file_size: Maximum file size in bytes (NEW)
        """
        self.code_dir = Path(code_dir)
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self.project_root = Path(project_root) if project_root else self.code_dir
        self.recursive = recursive
        self.max_file_size = max_file_size
        
        # Initialize storage
        self.python_files: Dict[str, str] = {}
        self.python_asts: Dict[str, ast.Module] = {}
        self.documents: Dict[str, str] = {}
        self.file_paths: Dict[str, Path] = {}  # Track original paths (NEW)
        
        # Setup ignore patterns (NEW)
        self.ignore_patterns = ignore_patterns or []
        self._load_gitignore()
    
    def _load_gitignore(self) -> None:
        """Load .gitignore patterns if present (NEW)."""
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.ignore_patterns.append(line)
            except Exception as e:
                print(f"Warning: Could not read .gitignore: {e}")
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored based on patterns (NEW)."""
        path_str = str(path)
        
        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path_str, pattern) or \
               fnmatch.fnmatch(path.name, pattern):
                return True
            
            # Check directory patterns
            for part in path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        
        return False
    
    def _is_file_too_large(self, file_path: Path) -> bool:
        """Check if file exceeds size limit (NEW)."""
        try:
            return file_path.stat().st_size > self.max_file_size
        except Exception:
            return False
    
    def ingest_python_files(self) -> int:
        """
        Read and parse all Python files.
        
        Returns:
            Number of files ingested
            
        NOTE: Now supports both flat and recursive modes
        """
        if self.recursive:
            py_files = self._find_python_files_recursive(self.code_dir)
        else:
            py_files = list(self.code_dir.glob("*.py"))
        
        for py_file in py_files:
            # Skip if should be ignored
            if self._should_ignore(py_file):
                continue
            
            # Skip if too large
            if self._is_file_too_large(py_file):
                print(f"⚠ Skipping {py_file.name}: File too large (>{self.max_file_size/1024/1024:.1f}MB)")
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # Use relative path as key for better organization
                relative_path = py_file.relative_to(self.code_dir) if self.recursive else py_file.name
                key = str(relative_path)
                
                self.python_files[key] = source_code
                self.file_paths[key] = py_file
                
                # Parse AST
                try:
                    parsed_ast = ast.parse(source_code, filename=str(py_file))
                    self.python_asts[key] = parsed_ast
                except SyntaxError as e:
                    print(f"⚠ Syntax error in {key}: {e}")
                    # Skip files with syntax errors - don't add to AST dict
                    continue
                
                print(f"✓ Ingested: {key}")
                
            except Exception as e:
                print(f"✗ Error ingesting {py_file.name}: {e}")
        
        return len(self.python_files)
    
    def _find_python_files_recursive(
        self, 
        directory: Path, 
        depth: int = 0, 
        max_depth: int = 10
    ) -> List[Path]:
        """
        Recursively find Python files in directory tree (NEW).
        
        Args:
            directory: Directory to search
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            
        Returns:
            List of Python file paths
        """
        if depth > max_depth:
            return []
        
        py_files: List[Path] = []
        
        try:
            for item in directory.iterdir():
                # Skip ignored items
                if self._should_ignore(item):
                    continue
                
                if item.is_file() and item.suffix == '.py':
                    py_files.append(item)
                elif item.is_dir():
                    py_files.extend(
                        self._find_python_files_recursive(item, depth + 1, max_depth)
                    )
        except PermissionError:
            print(f"⚠ Permission denied: {directory}")
        
        return py_files
    
    def ingest_documents(self) -> int:
        """
        Read all supporting documents (PDF and text files).
        
        Returns:
            Number of documents ingested
        """
        if not self.docs_dir or not self.docs_dir.exists():
            return 0
        
        if self.recursive:
            pdf_files = list(self.docs_dir.rglob("*.pdf"))
            txt_files = list(self.docs_dir.rglob("*.txt"))
            md_files = list(self.docs_dir.rglob("*.md"))
        else:
            pdf_files = list(self.docs_dir.glob("*.pdf"))
            txt_files = list(self.docs_dir.glob("*.txt"))
            md_files = list(self.docs_dir.glob("*.md"))
        
        # Process PDFs
        for pdf_file in pdf_files:
            if self._should_ignore(pdf_file) or self._is_file_too_large(pdf_file):
                continue
            
            text = extract_text_from_pdf(pdf_file)
            if text:
                key = str(pdf_file.relative_to(self.docs_dir)) if self.recursive else pdf_file.name
                self.documents[key] = text
                print(f"✓ Ingested: {key}")
        
        # Process text files
        for txt_file in txt_files + md_files:
            if self._should_ignore(txt_file) or self._is_file_too_large(txt_file):
                continue
            
            text = extract_text_from_txt(txt_file)
            if text:
                key = str(txt_file.relative_to(self.docs_dir)) if self.recursive else txt_file.name
                self.documents[key] = text
                print(f"✓ Ingested: {key}")
        
        return len(self.documents)
    
    def get_source_code(self, filename: str) -> Optional[str]:
        """Get source code for a specific file."""
        return self.python_files.get(filename)
    
    def get_ast(self, filename: str) -> Optional[ast.Module]:
        """Get AST for a specific file."""
        return self.python_asts.get(filename)
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        """Get original file path (NEW)."""
        return self.file_paths.get(filename)
    
    def get_all_source_files(self) -> Dict[str, str]:
        """Get all ingested source code files."""
        return self.python_files.copy()
    
    def get_all_documents(self) -> Dict[str, str]:
        """Get all ingested documents."""
        return self.documents.copy()
    
    def get_summary(self) -> Dict:
        """Get ingestion summary."""
        return {
            'python_files': list(self.python_files.keys()),
            'documents': list(self.documents.keys()),
            'total_files': len(self.python_files) + len(self.documents),
            'recursive_scan': self.recursive,  # NEW
            'project_root': str(self.project_root) if self.recursive else None  # NEW
        }
    
    def clear_cache(self) -> None:
        """Clear cached data to free memory (NEW)."""
        self.python_asts.clear()
        print("✓ Cache cleared")
