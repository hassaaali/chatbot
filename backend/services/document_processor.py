import re
import tiktoken
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def process_document(self, document: Dict) -> List[Dict]:
        """Process a document into chunks with metadata"""
        content = document['content']
        title = document['title']
        document_id = document['document_id']
        
        # Clean and preprocess text
        cleaned_content = self._clean_text(content)
        
        # Split into chunks
        chunks = self._split_text_into_chunks(cleaned_content)
        
        # Create chunk documents with metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_doc = {
                'content': chunk,
                'metadata': {
                    'source': 'google_docs',
                    'document_id': document_id,
                    'title': title,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'token_count': len(self.encoding.encode(chunk))
                }
            }
            processed_chunks.append(chunk_doc)
        
        logger.info(f"Processed document '{title}' into {len(chunks)} chunks")
        return processed_chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/]', '', text)
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        
        return text.strip()
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks based on token count"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Try to break at sentence boundaries
            if end < len(tokens):
                chunk_text = self._break_at_sentence_boundary(chunk_text)
            
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(tokens):
                break
        
        return chunks
    
    def _break_at_sentence_boundary(self, text: str) -> str:
        """Try to break chunk at a sentence boundary"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 1:
            # Remove the last incomplete sentence
            return '.'.join(sentences[:-1]) + '.'
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text for better retrieval"""
        # Simple keyword extraction - can be enhanced with NLP libraries
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'was', 'were', 'been', 'have', 'has', 'had', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'must', 'shall'
        }
        
        keywords = [word for word in words if word not in stop_words]
        
        # Return unique keywords, sorted by frequency
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(20)]