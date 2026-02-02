"""
File ingestion and parsing module
"""
from pathlib import Path
from typing import Dict, List, Optional
from utils.pdf_parser import extract_text_from_pdf, extract_text_from_txt
from utils.ast_helper import parse_python_file
import ast


class FileIngestion:
    """Handles ingestion of Python source files and supporting documents."""
    
    def __init__(self, code_dir: Path, docs_dir: Path):
        """
        Initialize the ingestion system.
        
        Args:
            code_dir: Directory containing Python source files
            docs_dir: Directory containing supporting documents
        """
        self.code_dir = code_dir
        self.docs_dir = docs_dir
        self.python_files: Dict[str, str] = {}
        self.python_asts: Dict[str, ast.Module] = {}
        self.documents: Dict[str, str] = {}
    
    def ingest_python_files(self) -> int:
        """
        Read and parse all Python files from the code directory.
        
        Returns:
            Number of files ingested
        """
        py_files = list(self.code_dir.glob("*.py"))
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                self.python_files[py_file.name] = source_code
                self.python_asts[py_file.name] = ast.parse(source_code, filename=str(py_file))
                print(f"✓ Ingested: {py_file.name}")
            except Exception as e:
                print(f"✗ Error ingesting {py_file.name}: {e}")
        
        return len(self.python_files)
    
    def ingest_documents(self) -> int:
        """
        Read all supporting documents (PDF and text files).
        
        Returns:
            Number of documents ingested
        """
        pdf_files = list(self.docs_dir.glob("*.pdf"))
        txt_files = list(self.docs_dir.glob("*.txt"))
        md_files = list(self.docs_dir.glob("*.md"))
        
        # Process PDFs
        for pdf_file in pdf_files:
            text = extract_text_from_pdf(pdf_file)
            if text:
                self.documents[pdf_file.name] = text
                print(f"✓ Ingested: {pdf_file.name}")
        
        # Process text files
        for txt_file in txt_files + md_files:
            text = extract_text_from_txt(txt_file)
            if text:
                self.documents[txt_file.name] = text
                print(f"✓ Ingested: {txt_file.name}")
        
        return len(self.documents)
    
    def get_source_code(self, filename: str) -> Optional[str]:
        """Get source code for a specific file."""
        return self.python_files.get(filename)
    
    def get_ast(self, filename: str) -> Optional[ast.Module]:
        """Get AST for a specific file."""
        return self.python_asts.get(filename)
    
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
            'total_files': len(self.python_files) + len(self.documents)
        }
