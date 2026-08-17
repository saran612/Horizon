import re
import os
from typing import List, Set
from pypdf import PdfReader

# Standard UUID regex pattern
UUID_PATTERN = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')

def extract_uuids_from_text(text: str) -> List[str]:
    """
    Extracts all unique UUIDs from the given text string.
    """
    if not text:
        return []
    # Find all matches and return as a sorted list of unique lowercase UUIDs
    matches: Set[str] = {match.lower() for match in UUID_PATTERN.findall(text)}
    return sorted(list(matches))

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF file using pypdf.
    """
    text_content = []
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        # Fallback or log error
        print(f"Error reading PDF: {e}")
    return "\n".join(text_content)

def extract_text_from_file(file_path: str, content_type: str = "") -> str:
    """
    Determines file type and extracts text accordingly.
    """
    if not os.path.exists(file_path):
        return ""
        
    ext = os.path.splitext(file_path)[1].lower()
    
    # PDF processing
    if ext == '.pdf' or 'pdf' in content_type.lower():
        return extract_text_from_pdf(file_path)
        
    # Text file processing
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text file: {e}")
        return ""
