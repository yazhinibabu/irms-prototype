"""
PDF text extraction utility
"""
import PyPDF2
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []
            
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            return "\n\n".join(text_content)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None


def extract_text_from_txt(txt_path: Path) -> Optional[str]:
    """
    Read text from a plain text file.
    
    Args:
        txt_path: Path to text file
        
    Returns:
        File content or None if reading fails
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text from {txt_path}: {e}")
        return None
