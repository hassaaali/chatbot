import re
from typing import List, Dict
from config import settings

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def process_document(self, doc_content: dict, document_id: str) -> List[Dict]:
        """Process document into chunks for vector storage"""
        text = doc_content['content']
        title = doc_content['title']
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Split into chunks
        chunks = self._split_text(cleaned_text)
        
        # Create document chunks with metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                'id': f"{document_id}_{i}",
                'content': chunk,
                'metadata': {
                    'document_id': document_id,
                    'title': title,
                    'chunk_index': i,
                    'source': f"Google Doc: {title}"
                }
            })
        
        return processed_chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove excessive whitespace
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
            
            # If we're not at the end, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', start, end)
                last_exclamation = text.rfind('!', start, end)
                last_question = text.rfind('?', start, end)
                
                sentence_end = max(last_period, last_exclamation, last_question)
                
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we don't go backwards
            if start <= 0:
                start = end
        
        return chunks