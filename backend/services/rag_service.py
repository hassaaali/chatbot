from typing import List, Dict, Optional
import logging
import gc
import psutil
from .vector_store import VectorStore
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, vector_store: VectorStore, document_processor: DocumentProcessor):
        self.vector_store = vector_store
        self.document_processor = document_processor
        self.documents = {}  # Store document metadata
    
    def add_document(self, document: Dict):
        """Add a document to the RAG system with detailed logging and memory monitoring"""
        document_id = None
        try:
            # Check memory before starting
            memory = psutil.virtual_memory()
            logger.info(f"Memory before RAG processing: {memory.percent}% used, {memory.available / (1024**3):.2f} GB available")
            
            if memory.percent > 75:
                raise Exception(f"Memory usage too high ({memory.percent}%) to safely process document")
            
            document_id = document['id']
            logger.info(f"Starting RAG processing for document: {document_id}")
            
            # Process document into chunks with memory monitoring
            logger.info("Processing document into chunks...")
            chunks = self.document_processor.process_document(document, document_id)
            logger.info(f"Document processed into {len(chunks)} chunks")
            
            # Check memory after chunking
            memory_after_chunks = psutil.virtual_memory()
            logger.info(f"Memory after chunking: {memory_after_chunks.percent}% used")
            
            if memory_after_chunks.percent > 80:
                logger.warning("High memory usage after chunking, forcing cleanup")
                gc.collect()
            
            # Limit number of chunks to prevent memory issues
            if len(chunks) > 10:
                logger.warning(f"Too many chunks ({len(chunks)}), limiting to first 10")
                chunks = chunks[:10]
            
            # Add chunks to vector store with detailed logging
            logger.info(f"Adding {len(chunks)} chunks to vector store...")
            self.vector_store.add_documents(chunks)
            logger.info("Successfully added chunks to vector store")
            
            # Store document metadata
            self.documents[document_id] = {
                'title': document['title'],
                'url': document.get('url', ''),
                'content_length': len(document['content']),
                'chunks_count': len(chunks)
            }
            
            logger.info(f"Successfully added document '{document['title']}' with {len(chunks)} chunks to RAG system")
            
            # Final memory check
            final_memory = psutil.virtual_memory()
            logger.info(f"Memory after RAG processing: {final_memory.percent}% used")
            
        except Exception as e:
            logger.error(f"Error adding document {document_id} to RAG system: {e}")
            # Try to cleanup on error
            if document_id and document_id in self.documents:
                try:
                    del self.documents[document_id]
                except:
                    pass
            raise
        finally:
            # Force cleanup
            gc.collect()
    
    def delete_document(self, document_id: str):
        """Remove a document from the RAG system"""
        try:
            logger.info(f"Removing document {document_id} from RAG system")
            
            # Remove from vector store
            self.vector_store.remove_document(document_id)
            
            # Remove from local metadata
            if document_id in self.documents:
                del self.documents[document_id]
            
            logger.info(f"Successfully removed document {document_id}")
            
        except Exception as e:
            logger.error(f"Error removing document {document_id}: {e}")
            raise
        finally:
            gc.collect()
    
    def clear_all_documents(self):
        """Clear all documents from the RAG system"""
        try:
            logger.info("Clearing all documents from RAG system")
            self.vector_store.clear_all()
            self.documents.clear()
            logger.info("Successfully cleared all documents")
            
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            raise
        finally:
            gc.collect()
    
    def retrieve_context(self, query: str, max_results: int = 2) -> List[Dict]:
        """Retrieve relevant context for a query with memory monitoring"""
        try:
            logger.info(f"Retrieving context for query: {query[:50]}...")
            
            # Check memory before retrieval
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                logger.warning(f"High memory usage ({memory.percent}%), limiting retrieval")
                max_results = 1
            
            results = self.vector_store.search(query, max_results)
            logger.info(f"Retrieved {len(results)} context results")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
        finally:
            gc.collect()
    
    def generate_rag_prompt(self, query: str, context_results: List[Dict]) -> str:
        """Generate an enhanced prompt with context for legal questions"""
        if not context_results:
            return self._generate_legal_prompt_without_context(query)
        
        # Build context from retrieved documents with length limits
        context_parts = []
        total_context_length = 0
        max_context_length = 1500  # Limit total context length
        
        for result in context_results:
            title = result['metadata'].get('title', 'Unknown Document')
            content = result['content']
            
            # Limit individual content length
            if len(content) > 500:
                content = content[:500] + "..."
            
            context_part = f"Document: '{title}'\nContent: {content}"
            
            # Check if adding this would exceed limit
            if total_context_length + len(context_part) > max_context_length:
                break
                
            context_parts.append(context_part)
            total_context_length += len(context_part)
        
        context = "\n\n".join(context_parts)
        
        # Create enhanced prompt for legal questions with length limits
        enhanced_prompt = f"""You are a knowledgeable legal assistant with expertise in analyzing legal documents and providing accurate legal information. Your role is to help users understand legal concepts, interpret documents, and provide guidance based on the provided legal materials.

IMPORTANT GUIDELINES:
1. Base your answers primarily on the provided legal documents
2. Clearly distinguish between what is stated in the documents vs. general legal knowledge
3. Use precise legal terminology when appropriate
4. If the documents don't contain sufficient information, clearly state this limitation
5. Always recommend consulting with a qualified attorney for specific legal advice
6. Cite specific sections or provisions when referencing the documents

LEGAL CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {query}

LEGAL ANALYSIS:
Please provide a comprehensive response that:
- Directly addresses the user's question using information from the provided documents
- Explains relevant legal concepts and terminology
- Identifies any applicable legal principles or precedents mentioned in the documents
- Notes any limitations or areas where additional legal consultation may be needed
- Provides clear, actionable guidance where appropriate

Response:"""
        
        # Limit total prompt length
        if len(enhanced_prompt) > 2000:
            enhanced_prompt = enhanced_prompt[:2000] + "...\n\nResponse:"
        
        return enhanced_prompt
    
    def _generate_legal_prompt_without_context(self, query: str) -> str:
        """Generate a legal prompt when no context documents are available"""
        return f"""You are a knowledgeable legal assistant. The user has asked a legal question, but no specific legal documents have been provided for context.

USER QUESTION: {query}

Please provide a helpful response that:
1. Addresses the legal question using general legal knowledge
2. Explains relevant legal concepts and terminology
3. Provides general guidance while emphasizing the importance of consulting with a qualified attorney
4. Suggests what types of legal documents or information would be helpful for a more specific analysis
5. Clearly states that this is general information and not specific legal advice

IMPORTANT: Always recommend consulting with a qualified attorney for specific legal advice tailored to the user's particular situation.

Response:"""
    
    def get_system_stats(self) -> Dict:
        """Get RAG system statistics with memory information"""
        try:
            vector_stats = self.vector_store.get_stats()
            memory = psutil.virtual_memory()
            
            # Calculate sources breakdown
            sources = {}
            for doc_id, doc_info in self.documents.items():
                title = doc_info['title']
                sources[title] = doc_info['chunks_count']
            
            return {
                'vector_store_stats': {
                    'total_documents': len(self.documents),
                    'total_chunks': vector_stats['total_chunks'],
                    'embedding_model': vector_stats['embedding_model'],
                    'sources': sources,
                    'memory_usage_percent': memory.percent,
                    'available_memory_gb': memory.available / (1024**3)
                },
                'processor_config': {
                    'chunk_size': self.document_processor.chunk_size,
                    'chunk_overlap': self.document_processor.chunk_overlap
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'vector_store_stats': {
                    'total_documents': 0,
                    'total_chunks': 0,
                    'embedding_model': 'unknown',
                    'sources': {},
                    'memory_usage_percent': 0,
                    'available_memory_gb': 0
                },
                'processor_config': {
                    'chunk_size': 300,
                    'chunk_overlap': 50
                }
            }