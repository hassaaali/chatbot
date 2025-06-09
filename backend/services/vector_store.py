import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Optional
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
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
            metadata={"description": "Document chunks for RAG"}
        )
        
        logger.info(f"Vector store initialized with {self.collection.count()} documents")
    
    def add_documents(self, documents: List[Dict]) -> None:
        """Add documents to the vector store"""
        if not documents:
            return
        
        texts = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Generate unique IDs
        ids = [str(uuid.uuid4()) for _ in documents]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            result = {
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
            }
            formatted_results.append(result)
        
        logger.info(f"Retrieved {len(formatted_results)} results for query")
        return formatted_results
    
    def delete_document(self, document_id: str) -> None:
        """Delete all chunks from a specific document"""
        # Get all documents with the specified document_id
        results = self.collection.get(
            where={"document_id": document_id},
            include=['metadatas']
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        
        # Get sample of documents to analyze
        sample_results = self.collection.get(
            limit=min(100, count),
            include=['metadatas']
        )
        
        # Analyze document sources
        sources = {}
        for metadata in sample_results['metadatas']:
            source = metadata.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_documents': count,
            'sources': sources,
            'embedding_model': self.embedding_model_name
        }
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection"""
        # Delete the collection and recreate it
        self.client.delete_collection("documents")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Document chunks for RAG"}
        )
        logger.info("Cleared all documents from vector store")