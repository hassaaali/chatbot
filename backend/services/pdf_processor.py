import io
import logging
import gc
from typing import Dict, List, Optional
import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.supported_mimetypes = [
            'application/pdf'
        ]
    
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> str:
        """Extract text from PDF bytes using multiple methods with memory optimization"""
        text = ""
        pdf_io = None
        
        try:
            # Method 1: Try pdfplumber first (better for complex layouts)
            try:
                pdf_io = io.BytesIO(pdf_bytes)
                with pdfplumber.open(pdf_io) as pdf:
                    page_texts = []
                    max_pages = min(len(pdf.pages), 50)  # Limit to 50 pages to avoid memory issues
                    
                    for page_num in range(max_pages):
                        try:
                            page = pdf.pages[page_num]
                            page_text = page.extract_text()
                            if page_text:
                                page_texts.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
                            
                            # Force garbage collection every 10 pages
                            if page_num % 10 == 0:
                                gc.collect()
                                
                        except Exception as e:
                            logger.warning(f"pdfplumber failed on page {page_num + 1} of {filename}: {e}")
                            continue
                    
                    text = "\n".join(page_texts)
                    
                if text.strip():
                    logger.info(f"Successfully extracted {len(text)} characters from {filename} using pdfplumber")
                    return text.strip()
                    
            except Exception as e:
                logger.warning(f"pdfplumber failed for {filename}: {e}")
            finally:
                if pdf_io:
                    pdf_io.close()
                    pdf_io = None
                gc.collect()
            
            # Method 2: Fallback to PyPDF2
            try:
                pdf_io = io.BytesIO(pdf_bytes)
                pdf_reader = PyPDF2.PdfReader(pdf_io)
                page_texts = []
                max_pages = min(len(pdf_reader.pages), 50)  # Limit to 50 pages
                
                for page_num in range(max_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
                        
                        # Force garbage collection every 10 pages
                        if page_num % 10 == 0:
                            gc.collect()
                            
                    except Exception as e:
                        logger.warning(f"PyPDF2 failed on page {page_num + 1} of {filename}: {e}")
                        continue
                
                text = "\n".join(page_texts)
                
                if text.strip():
                    logger.info(f"Successfully extracted {len(text)} characters from {filename} using PyPDF2")
                    return text.strip()
                    
            except Exception as e:
                logger.warning(f"PyPDF2 failed for {filename}: {e}")
            finally:
                if pdf_io:
                    pdf_io.close()
                    pdf_io = None
                gc.collect()
            
            # If both methods fail
            logger.error(f"Failed to extract text from {filename} using all available methods")
            raise Exception(f"Could not extract text from PDF: {filename}")
            
        finally:
            # Final cleanup
            if pdf_io:
                pdf_io.close()
            gc.collect()
    
    def is_supported_file(self, mimetype: str) -> bool:
        """Check if the file type is supported"""
        return mimetype in self.supported_mimetypes
    
    def get_file_info(self, file_metadata: Dict) -> Dict:
        """Extract relevant information from file metadata"""
        return {
            'id': file_metadata['id'],
            'title': file_metadata['name'],
            'mimetype': file_metadata.get('mimeType', ''),
            'size': int(file_metadata.get('size', 0)),
            'modified_time': file_metadata.get('modifiedTime'),
            'url': file_metadata.get('webViewLink', f"https://drive.google.com/file/d/{file_metadata['id']}/view"),
            'download_url': f"https://drive.google.com/uc?id={file_metadata['id']}&export=download"
        }