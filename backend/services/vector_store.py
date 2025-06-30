import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import uuid
import gc
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_path: str, embedding_model: str):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        
        try:
            # Initialize ChromaDB with memory optimization
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize embedding model with memory optimization
            logger.info(f"Loading embedding model: {embedding_model}")
            self.embedding_model = SentenceTransformer(
                embedding_model,
                device='cpu'  # Force CPU to avoid GPU memory issues
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store with memory optimization"""
        try:
            if not documents:
                return
            
            # Process in smaller batches to avoid memory issues
            batch_size = 5  # Reduced batch size
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                texts = [doc['content'] for doc in batch]
                metadatas = [doc['metadata'] for doc in batch]
                ids = [doc['id'] for doc in batch]
                
                # Generate embeddings for this batch
                logger.info(f"Generating embeddings for batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
                embeddings = self.embedding_model.encode(
                    texts, 
                    batch_size=2,  # Very small batch size for encoding
                    show_progress_bar=False,
                    convert_to_numpy=True
                ).tolist()
                
                # Add to collection
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                # Force garbage collection after each batch
                gc.collect()
                
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for similar documents with memory optimization"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                [query], 
                show_progress_bar=False,
                convert_to_numpy=True
            ).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=min(n_results, 3)  # Limit results to avoid memory issues
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def remove_document(self, document_id: str):
        """Remove all chunks of a document"""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"source_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Removed {len(results['ids'])} chunks for document {document_id}")
                
        except Exception as e:
            logger.error(f"Error removing document {document_id}: {e}")
            raise
    
    def clear_all(self):
        """Clear all documents from the vector store"""
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            gc.collect()  # Force garbage collection
            logger.info("Cleared all documents from vector store")
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "embedding_model": self.embedding_model_name,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {
                "total_chunks": 0,
                "embedding_model": self.embedding_model_name,
                "db_path": self.db_path
            }