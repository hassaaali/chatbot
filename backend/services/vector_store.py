import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import uuid

from config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer(settings.embedding_model)
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store"""
        if not documents:
            return
        
        # Extract content and metadata
        contents = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        ids = [doc['id'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(contents).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = None) -> List[Dict]:
        """Search for similar documents"""
        if n_results is None:
            n_results = settings.max_retrieval_results
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return formatted_results
    
    def remove_document(self, document_id: str):
        """Remove all chunks of a document"""
        # Get all chunks for this document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def clear_all(self):
        """Clear all documents from the vector store"""
        self.collection.delete()
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "embedding_model": settings.embedding_model
        }