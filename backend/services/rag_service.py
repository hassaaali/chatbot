from typing import List, Dict, Optional
import logging
from .vector_store import VectorStore
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, vector_store: VectorStore, document_processor: DocumentProcessor):
        self.vector_store = vector_store
        self.document_processor = document_processor
    
    def add_document(self, document: Dict) -> None:
        """Process and add a document to the RAG system"""
        try:
            # Process document into chunks
            processed_chunks = self.document_processor.process_document(document)
            
            # Add to vector store
            self.vector_store.add_documents(processed_chunks)
            
            logger.info(f"Successfully added document '{document['title']}' to RAG system")
        except Exception as e:
            logger.error(f"Error adding document to RAG system: {e}")
            raise
    
    def retrieve_context(self, query: str, max_results: int = 5) -> List[Dict]:
        """Retrieve relevant context for a query"""
        try:
            results = self.vector_store.search(query, n_results=max_results)
            
            # Filter results by relevance threshold
            relevant_results = [
                result for result in results 
                if result['similarity_score'] > 0.3  # Adjust threshold as needed
            ]
            
            logger.info(f"Retrieved {len(relevant_results)} relevant contexts for query")
            return relevant_results
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def generate_rag_prompt(self, query: str, context_results: List[Dict]) -> str:
        """Generate an enhanced prompt with retrieved context"""
        if not context_results:
            return query
        
        # Build context section
        context_sections = []
        for i, result in enumerate(context_results, 1):
            content = result['content']
            metadata = result['metadata']
            title = metadata.get('title', 'Unknown Document')
            
            context_section = f"""
Context {i} (from "{title}"):
{content}
"""
            context_sections.append(context_section)
        
        # Combine into RAG prompt
        rag_prompt = f"""You are an AI assistant that answers questions based on the provided context. Use the following context to answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

CONTEXT:
{''.join(context_sections)}

QUESTION: {query}

Please provide a comprehensive answer based on the context above. If you reference specific information, mention which document it came from.

ANSWER:"""
        
        return rag_prompt
    
    def get_system_stats(self) -> Dict:
        """Get statistics about the RAG system"""
        return {
            'vector_store_stats': self.vector_store.get_collection_stats(),
            'processor_config': {
                'chunk_size': self.document_processor.chunk_size,
                'chunk_overlap': self.document_processor.chunk_overlap
            }
        }
    
    def delete_document(self, document_id: str) -> None:
        """Remove a document from the RAG system"""
        self.vector_store.delete_document(document_id)
        logger.info(f"Removed document {document_id} from RAG system")
    
    def clear_all_documents(self) -> None:
        """Clear all documents from the RAG system"""
        self.vector_store.clear_collection()
        logger.info("Cleared all documents from RAG system")