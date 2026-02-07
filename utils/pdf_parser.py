"""
PDF and text file parsing utilities
"""
from pathlib import Path
from typing import Optional

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if extraction fails
    """
    if not PDF_AVAILABLE:
        print(f"⚠ PyPDF2 not available, skipping {pdf_path.name}")
        return None
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_parts = []
            
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            
            return '\n'.join(text_parts)
    except Exception as e:
        print(f"⚠ Error reading PDF {pdf_path.name}: {e}")
        return None


def extract_text_from_txt(txt_path: Path) -> Optional[str]:
    """
    Extract text content from a text file.
    
    Args:
        txt_path: Path to text file
        
    Returns:
        File content or None if read fails
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(txt_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            print(f"⚠ Error reading text file {txt_path.name}: {e}")
            return None
    except Exception as e:
        print(f"⚠ Error reading text file {txt_path.name}: {e}")
        return None