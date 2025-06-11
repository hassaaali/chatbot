import re
from typing import List, Dict

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, document: Dict, document_id: str) -> List[Dict]:
        """Process a document into chunks with metadata"""
        content = document['content']
        title = document['title']
        url = document['url']
        
        # Clean the text
        cleaned_content = self._clean_text(content)
        
        # Split into chunks
        chunks = self._split_text(cleaned_content)
        
        # Create chunk documents with metadata
        chunk_documents = []
        for i, chunk in enumerate(chunks):
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
        
        return chunk_documents
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the overlap region
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks