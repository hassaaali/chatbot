import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import uuid
import gc
import logging
import os
import psutil

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_path: str, embedding_model: str):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        
        try:
            # Check available memory before initialization
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            logger.info(f"Available memory: {available_gb:.2f} GB")
            
            if available_gb < 1.0:
                logger.warning("Low memory detected, using minimal configuration")
            
            # Initialize ChromaDB with aggressive memory optimization
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    persist_directory=db_path
                )
            )
            
            # Initialize embedding model with strict memory limits
            logger.info(f"Loading lightweight embedding model: {embedding_model}")
            self.embedding_model = SentenceTransformer(
                embedding_model,
                device='cpu',  # Force CPU to avoid GPU memory issues
                cache_folder=None  # Don't cache to save memory
            )
            
            # Reduce model precision to save memory
            self.embedding_model.half()  # Use half precision
            
            # Get or create collection with minimal settings
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine", "hnsw:M": 8}  # Reduced M parameter
            )
            
            logger.info("Vector store initialized with memory optimization")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store with aggressive memory optimization"""
        try:
            if not documents:
                return
            
            # Process in very small batches to avoid memory issues
            batch_size = 1  # Process one document at a time
            
            for i, doc in enumerate(documents):
                try:
                    logger.info(f"Processing document {i+1}/{len(documents)}")
                    
                    # Check memory before processing each document
                    memory = psutil.virtual_memory()
                    if memory.percent > 85:
                        logger.warning(f"High memory usage ({memory.percent}%), forcing cleanup")
                        gc.collect()
                        
                        # If still high memory, skip this document
                        if psutil.virtual_memory().percent > 90:
                            logger.error(f"Memory too high, skipping document {i+1}")
                            continue
                    
                    text = doc['content']
                    metadata = doc['metadata']
                    doc_id = doc['id']
                    
                    # Truncate very long texts to prevent memory issues
                    if len(text) > 1000:
                        text = text[:1000] + "..."
                        logger.warning(f"Truncated long text for document {doc_id}")
                    
                    # Generate embedding for single document
                    embedding = self.embedding_model.encode(
                        [text], 
                        batch_size=1,
                        show_progress_bar=False,
                        convert_to_numpy=True,
                        normalize_embeddings=True  # Normalize to save space
                    ).tolist()
                    
                    # Add to collection immediately
                    self.collection.add(
                        embeddings=embedding,
                        documents=[text],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                    
                    # Force garbage collection after each document
                    del embedding, text
                    gc.collect()
                    
                    logger.info(f"Successfully added document {i+1}/{len(documents)}")
                    
                except Exception as e:
                    logger.error(f"Error processing document {i+1}: {e}")
                    continue
                
            logger.info(f"Completed processing {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
        finally:
            # Final cleanup
            gc.collect()
    
    def search(self, query: str, n_results: int = 2) -> List[Dict]:
        """Search for similar documents with memory optimization"""
        try:
            # Limit query length to prevent memory issues
            if len(query) > 500:
                query = query[:500]
            
            # Generate query embedding with minimal memory usage
            query_embedding = self.embedding_model.encode(
                [query], 
                batch_size=1,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            ).tolist()
            
            # Search in collection with limited results
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=min(n_results, 2)  # Limit to 2 results max
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
            
            # Cleanup
            del query_embedding
            gc.collect()
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
        finally:
            gc.collect()
    
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
        finally:
            gc.collect()
    
    def clear_all(self):
        """Clear all documents from the vector store"""
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine", "hnsw:M": 8}
            )
            gc.collect()
            logger.info("Cleared all documents from vector store")
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
        finally:
            gc.collect()
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        try:
            count = self.collection.count()
            memory = psutil.virtual_memory()
            return {
                "total_chunks": count,
                "embedding_model": self.embedding_model_name,
                "db_path": self.db_path,
                "memory_usage_percent": memory.percent,
                "available_memory_gb": memory.available / (1024**3)
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {
                "total_chunks": 0,
                "embedding_model": self.embedding_model_name,
                "db_path": self.db_path,
                "memory_usage_percent": 0,
                "available_memory_gb": 0
            }