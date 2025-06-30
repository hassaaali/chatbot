import os
import tempfile
import logging
import gc
import psutil
from typing import Dict, Optional
from fastapi import UploadFile
import magic
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

class FileUploadService:
    def __init__(self, max_file_size: int = 5 * 1024 * 1024):  # Reduced to 5MB
        self.max_file_size = max_file_size
        self.pdf_processor = PDFProcessor()
        self.allowed_mime_types = [
            'application/pdf',
            'application/x-pdf'
        ]
    
    def validate_file(self, file: UploadFile) -> Dict[str, any]:
        """Validate uploaded file with memory checks"""
        validation_result = {
            'valid': False,
            'error': None,
            'file_info': {}
        }
        
        try:
            # Check available memory first
            memory = psutil.virtual_memory()
            if memory.percent > 75:
                validation_result['error'] = f"System memory too high ({memory.percent}%). Please try again later."
                return validation_result
            
            # Check filename
            if not file.filename:
                validation_result['error'] = "No filename provided"
                return validation_result
            
            # Check file extension
            if not file.filename.lower().endswith('.pdf'):
                validation_result['error'] = "Only PDF files are supported"
                return validation_result
            
            validation_result['valid'] = True
            validation_result['file_info'] = {
                'filename': file.filename,
                'content_type': file.content_type,
                'size': getattr(file, 'size', 0)
            }
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            validation_result['error'] = f"File validation error: {str(e)}"
        
        return validation_result
    
    async def process_uploaded_pdf(self, file: UploadFile, custom_title: Optional[str] = None) -> Dict:
        """Process uploaded PDF file with aggressive memory optimization"""
        file_content = None
        try:
            # Check memory before starting
            memory = psutil.virtual_memory()
            logger.info(f"Memory before processing: {memory.percent}% used, {memory.available / (1024**3):.2f} GB available")
            
            if memory.percent > 70:
                raise Exception(f"Insufficient memory available ({memory.percent}% used). Please close other applications and try again.")
            
            logger.info(f"Starting to process uploaded PDF: {file.filename}")
            
            # Validate file first
            validation = self.validate_file(file)
            if not validation['valid']:
                raise Exception(validation['error'])
            
            logger.info(f"File validation passed for: {file.filename}")
            
            # Read file content in very small chunks
            logger.info("Reading file content...")
            file_content = await self._read_file_safely(file)
            file_size = len(file_content)
            
            logger.info(f"File content read successfully. Size: {file_size} bytes")
            
            # Check file size after reading
            if file_size > self.max_file_size:
                raise Exception(f"File size ({file_size} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)")
            
            if file_size == 0:
                raise Exception("File appears to be empty")
            
            # Check memory after reading file
            memory_after_read = psutil.virtual_memory()
            if memory_after_read.percent > 80:
                raise Exception(f"Memory usage too high after reading file ({memory_after_read.percent}%). File may be too large.")
            
            # Validate MIME type using python-magic (optional, minimal check)
            try:
                logger.info("Validating MIME type...")
                # Only check first 1024 bytes to save memory
                mime_type = magic.from_buffer(file_content[:1024], mime=True)
                logger.info(f"Detected MIME type: {mime_type}")
                if mime_type not in self.allowed_mime_types:
                    logger.warning(f"Unexpected MIME type: {mime_type}, but continuing since extension is .pdf")
            except Exception as e:
                logger.warning(f"Could not validate MIME type (python-magic may not be available): {e}")
            
            # Extract text from PDF with aggressive memory optimization
            logger.info("Extracting text from PDF...")
            text_content = self.pdf_processor.extract_text_from_pdf_bytes(
                file_content, 
                file.filename
            )
            
            # Clear file content from memory immediately after processing
            del file_content
            file_content = None
            gc.collect()  # Force garbage collection
            
            logger.info(f"Text extraction completed. Extracted {len(text_content)} characters")
            
            if not text_content.strip():
                raise Exception("No text content could be extracted from the PDF. The file may be image-based or corrupted.")
            
            # Limit text content length to prevent memory issues
            if len(text_content) > 3000:
                text_content = text_content[:3000] + "\n\n[Content truncated due to memory constraints]"
                logger.info("Text content truncated to prevent memory issues")
            
            # Generate document ID from filename and content hash
            import hashlib
            content_hash = hashlib.md5(text_content.encode()).hexdigest()[:8]
            safe_filename = file.filename.replace('.pdf', '').replace(' ', '_').replace('/', '_').replace('\\', '_')
            document_id = f"upload_{content_hash}_{safe_filename}"
            
            # Prepare document object
            document = {
                'id': document_id,
                'title': custom_title or file.filename.replace('.pdf', ''),
                'content': text_content,
                'url': f"local://uploaded/{file.filename}",
                'size': file_size,
                'mimetype': 'application/pdf',
                'source': 'upload',
                'filename': file.filename
            }
            
            logger.info(f"Successfully processed uploaded PDF: {file.filename} ({len(text_content)} characters)")
            
            # Final memory check
            final_memory = psutil.virtual_memory()
            logger.info(f"Memory after processing: {final_memory.percent}% used")
            
            return document
            
        except Exception as e:
            logger.error(f"Error processing uploaded PDF {file.filename}: {e}")
            raise Exception(f"Failed to process PDF: {str(e)}")
        finally:
            # Cleanup memory
            if file_content is not None:
                del file_content
            gc.collect()
            
            # Reset file pointer for potential reuse
            try:
                await file.seek(0)
            except Exception as e:
                logger.warning(f"Could not reset file pointer: {e}")
    
    async def _read_file_safely(self, file: UploadFile) -> bytes:
        """Read file content safely in very small chunks to avoid memory issues"""
        content = bytearray()
        chunk_size = 4096  # Reduced to 4KB chunks
        
        try:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                content.extend(chunk)
                
                # Check memory usage during reading
                memory = psutil.virtual_memory()
                if memory.percent > 85:
                    raise Exception(f"Memory usage too high during file reading ({memory.percent}%)")
                
                # Check if we're exceeding file size limits
                if len(content) > self.max_file_size:
                    raise Exception(f"File too large (exceeds {self.max_file_size} bytes)")
            
            return bytes(content)
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise
        finally:
            # Force cleanup
            if 'content' in locals():
                del content
            gc.collect()