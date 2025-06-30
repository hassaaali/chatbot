import io
import logging
import gc
import psutil
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
        """Extract text from PDF bytes using memory-optimized methods"""
        text = ""
        pdf_io = None
        
        try:
            # Check available memory before processing
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            logger.info(f"Available memory before PDF processing: {available_gb:.2f} GB")
            
            if available_gb < 0.5:
                raise Exception("Insufficient memory available for PDF processing")
            
            # Method 1: Try pdfplumber with strict limits
            try:
                pdf_io = io.BytesIO(pdf_bytes)
                with pdfplumber.open(pdf_io) as pdf:
                    page_texts = []
                    # Severely limit pages to prevent memory issues
                    max_pages = min(len(pdf.pages), 10)  # Only process first 10 pages
                    
                    for page_num in range(max_pages):
                        try:
                            # Check memory before each page
                            if psutil.virtual_memory().percent > 80:
                                logger.warning(f"High memory usage, stopping at page {page_num}")
                                break
                            
                            page = pdf.pages[page_num]
                            page_text = page.extract_text()
                            
                            if page_text:
                                # Limit text length per page
                                if len(page_text) > 2000:
                                    page_text = page_text[:2000] + "..."
                                page_texts.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
                            
                            # Force cleanup after each page
                            del page_text
                            gc.collect()
                                
                        except Exception as e:
                            logger.warning(f"pdfplumber failed on page {page_num + 1} of {filename}: {e}")
                            continue
                    
                    text = "\n".join(page_texts)
                    
                    # Limit total text length
                    if len(text) > 5000:
                        text = text[:5000] + "\n\n[Text truncated due to memory constraints]"
                    
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
            
            # Method 2: Fallback to PyPDF2 with strict limits
            try:
                pdf_io = io.BytesIO(pdf_bytes)
                pdf_reader = PyPDF2.PdfReader(pdf_io)
                page_texts = []
                # Even more restrictive for PyPDF2
                max_pages = min(len(pdf_reader.pages), 5)  # Only 5 pages max
                
                for page_num in range(max_pages):
                    try:
                        # Check memory before each page
                        if psutil.virtual_memory().percent > 80:
                            logger.warning(f"High memory usage, stopping at page {page_num}")
                            break
                        
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text:
                            # Limit text length per page
                            if len(page_text) > 1500:
                                page_text = page_text[:1500] + "..."
                            page_texts.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
                        
                        # Force cleanup after each page
                        del page_text
                        gc.collect()
                            
                    except Exception as e:
                        logger.warning(f"PyPDF2 failed on page {page_num + 1} of {filename}: {e}")
                        continue
                
                text = "\n".join(page_texts)
                
                # Limit total text length
                if len(text) > 3000:
                    text = text[:3000] + "\n\n[Text truncated due to memory constraints]"
                
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
            del pdf_bytes  # Explicitly delete the bytes
            gc.collect()
            
            # Log final memory state
            final_memory = psutil.virtual_memory()
            logger.info(f"Memory after PDF processing: {final_memory.percent}% used")
    
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