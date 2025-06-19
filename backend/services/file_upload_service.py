import os
import tempfile
import logging
from typing import Dict, Optional
from fastapi import UploadFile
import magic
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

class FileUploadService:
    def __init__(self, max_file_size: int = 50 * 1024 * 1024):  # 50MB default
        self.max_file_size = max_file_size
        self.pdf_processor = PDFProcessor()
        self.allowed_mime_types = [
            'application/pdf',
            'application/x-pdf'
        ]
    
    def validate_file(self, file: UploadFile) -> Dict[str, any]:
        """Validate uploaded file"""
        validation_result = {
            'valid': False,
            'error': None,
            'file_info': {}
        }
        
        try:
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
        """Process uploaded PDF file and extract content"""
        try:
            logger.info(f"Starting to process uploaded PDF: {file.filename}")
            
            # Validate file first
            validation = self.validate_file(file)
            if not validation['valid']:
                raise Exception(validation['error'])
            
            logger.info(f"File validation passed for: {file.filename}")
            
            # Read file content
            logger.info("Reading file content...")
            file_content = await file.read()
            file_size = len(file_content)
            
            logger.info(f"File content read successfully. Size: {file_size} bytes")
            
            # Check file size after reading
            if file_size > self.max_file_size:
                raise Exception(f"File size ({file_size} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)")
            
            if file_size == 0:
                raise Exception("File appears to be empty")
            
            # Validate MIME type using python-magic (optional, don't fail if magic is not available)
            try:
                logger.info("Validating MIME type...")
                mime_type = magic.from_buffer(file_content, mime=True)
                logger.info(f"Detected MIME type: {mime_type}")
                if mime_type not in self.allowed_mime_types:
                    logger.warning(f"Unexpected MIME type: {mime_type}, but continuing since extension is .pdf")
            except Exception as e:
                logger.warning(f"Could not validate MIME type (python-magic may not be available): {e}")
                # Continue if magic fails, rely on extension check
            
            # Extract text from PDF
            logger.info("Extracting text from PDF...")
            text_content = self.pdf_processor.extract_text_from_pdf_bytes(
                file_content, 
                file.filename
            )
            
            logger.info(f"Text extraction completed. Extracted {len(text_content)} characters")
            
            if not text_content.strip():
                raise Exception("No text content could be extracted from the PDF. The file may be image-based or corrupted.")
            
            # Generate document ID from filename and content hash
            import hashlib
            content_hash = hashlib.md5(file_content).hexdigest()[:8]
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
            return document
            
        except Exception as e:
            logger.error(f"Error processing uploaded PDF {file.filename}: {e}")
            raise Exception(f"Failed to process PDF: {str(e)}")
        finally:
            # Reset file pointer for potential reuse
            try:
                await file.seek(0)
            except Exception as e:
                logger.warning(f"Could not reset file pointer: {e}")