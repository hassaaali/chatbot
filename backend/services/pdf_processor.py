import io
import logging
from typing import Dict, List, Optional
import PyPDF2
import pdfplumber
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.supported_mimetypes = [
            'application/pdf'
        ]
    
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> str:
        """Extract text from PDF bytes using multiple methods for best results"""
        text = ""
        
        # Method 1: Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"pdfplumber failed on page {page_num + 1} of {filename}: {e}")
                        continue
                        
            if text.strip():
                logger.info(f"Successfully extracted {len(text)} characters from {filename} using pdfplumber")
                return text.strip()
                
        except Exception as e:
            logger.warning(f"pdfplumber failed for {filename}: {e}")
        
        # Method 2: Fallback to PyPDF2
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"PyPDF2 failed on page {page_num + 1} of {filename}: {e}")
                    continue
            
            if text.strip():
                logger.info(f"Successfully extracted {len(text)} characters from {filename} using PyPDF2")
                return text.strip()
                
        except Exception as e:
            logger.warning(f"PyPDF2 failed for {filename}: {e}")
        
        # If both methods fail
        logger.error(f"Failed to extract text from {filename} using all available methods")
        raise Exception(f"Could not extract text from PDF: {filename}")
    
    def is_supported_file(self, mimetype: str) -> bool:
        """Check if the file type is supported"""
        return mimetype in self.supported_mimetypes
    
    def get_file_info(self, file_metadata: Dict) -> Dict:
        """Extract relevant information from Google Drive file metadata"""
        return {
            'id': file_metadata['id'],
            'title': file_metadata['name'],
            'mimetype': file_metadata.get('mimeType', ''),
            'size': int(file_metadata.get('size', 0)),
            'modified_time': file_metadata.get('modifiedTime'),
            'url': file_metadata.get('webViewLink', f"https://drive.google.com/file/d/{file_metadata['id']}/view"),
            'download_url': f"https://drive.google.com/uc?id={file_metadata['id']}&export=download"
        }