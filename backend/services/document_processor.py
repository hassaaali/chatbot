import re
import gc
import logging
import psutil
from typing import List, Dict

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, document: Dict, document_id: str) -> List[Dict]:
        """Process a document into chunks with metadata and memory monitoring"""
        try:
            # Check memory before processing
            memory = psutil.virtual_memory()
            logger.info(f"Memory before document processing: {memory.percent}% used")
            
            if memory.percent > 80:
                raise Exception(f"Memory usage too high ({memory.percent}%) for document processing")
            
            content = document['content']
            title = document['title']
            url = document['url']
            
            logger.info(f"Processing document '{title}' with {len(content)} characters")
            
            # Limit content length to prevent memory issues
            if len(content) > 2000:
                content = content[:2000] + "..."
                logger.warning(f"Content truncated to 2000 characters for memory efficiency")
            
            # Clean the text
            logger.info("Cleaning text...")
            cleaned_content = self._clean_text(content)
            
            # Split into chunks
            logger.info("Splitting into chunks...")
            chunks = self._split_text(cleaned_content)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Limit number of chunks
            if len(chunks) > 8:
                chunks = chunks[:8]
                logger.warning(f"Limited to first 8 chunks for memory efficiency")
            
            # Create chunk documents with metadata
            chunk_documents = []
            for i, chunk in enumerate(chunks):
                # Limit individual chunk size
                if len(chunk) > 400:
                    chunk = chunk[:400] + "..."
                
                chunk_doc = {
                    'id': f"{document_id}_chunk_{i}",
                    'content': chunk,
                    'metadata': {
                        'source_id': document_id,
                        'title': title,
                        'url': url,
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                }
                chunk_documents.append(chunk_doc)
                
                # Force cleanup every few chunks
                if i % 3 == 0:
                    gc.collect()
            
            logger.info(f"Successfully processed document into {len(chunk_documents)} chunks")
            return chunk_documents
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            raise
        finally:
            # Cleanup
            gc.collect()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text with memory efficiency"""
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
            return text.strip()
        except Exception as e:
            logger.warning(f"Error cleaning text: {e}")
            return text.strip()
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks with memory efficiency"""
        try:
            if len(text) <= self.chunk_size:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(text) and len(chunks) < 10:  # Limit total chunks
                end = start + self.chunk_size
                
                # If this is not the last chunk, try to break at a sentence boundary
                if end < len(text):
                    # Look for sentence endings within the overlap region
                    sentence_end = text.rfind('.', start, end)
                    if sentence_end > start:
                        end = sentence_end + 1
                
                chunk = text[start:end].strip()
                if chunk and len(chunk) > 10:  # Only add meaningful chunks
                    chunks.append(chunk)
                
                # Move start position with overlap
                start = end - self.chunk_overlap
                if start >= len(text):
                    break
                
                # Force cleanup every few iterations
                if len(chunks) % 3 == 0:
                    gc.collect()
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            # Return the original text as a single chunk if splitting fails
            return [text[:self.chunk_size]]