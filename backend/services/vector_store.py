import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import uuid

class VectorStore:
    def __init__(self, db_path: str, embedding_model: str):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store"""
        texts = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        ids = [doc['id'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            result = {
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def remove_document(self, document_id: str):
        """Remove all chunks of a document"""
        # Get all chunks for this document
        results = self.collection.get(
            where={"source_id": document_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def clear_all(self):
        """Clear all documents from the vector store"""
        self.client.delete_collection("documents")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "embedding_model": self.embedding_model_name,
            "db_path": self.db_path
        }