from typing import List, Dict, Optional
import logging
from .vector_store import VectorStore
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, vector_store: VectorStore, document_processor: DocumentProcessor):
        self.vector_store = vector_store
        self.document_processor = document_processor
        self.documents = {}  # Store document metadata
    
    def add_document(self, document: Dict):
        """Add a document to the RAG system"""
        try:
            document_id = document['id']
            
            # Process document into chunks
            chunks = self.document_processor.process_document(document, document_id)
            
            # Add chunks to vector store
            self.vector_store.add_documents(chunks)
            
            # Store document metadata
            self.documents[document_id] = {
                'title': document['title'],
                'url': document.get('url', ''),
                'content_length': len(document['content']),
                'chunks_count': len(chunks)
            }
            
            logger.info(f"Added document '{document['title']}' with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def delete_document(self, document_id: str):
        """Remove a document from the RAG system"""
        try:
            # Remove from vector store
            self.vector_store.remove_document(document_id)
            
            # Remove from local metadata
            if document_id in self.documents:
                del self.documents[document_id]
            
            logger.info(f"Removed document {document_id}")
            
        except Exception as e:
            logger.error(f"Error removing document: {e}")
            raise
    
    def clear_all_documents(self):
        """Clear all documents from the RAG system"""
        try:
            self.vector_store.clear_all()
            self.documents.clear()
            logger.info("Cleared all documents")
            
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            raise
    
    def retrieve_context(self, query: str, max_results: int = 5) -> List[Dict]:
        """Retrieve relevant context for a query"""
        try:
            results = self.vector_store.search(query, max_results)
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def generate_rag_prompt(self, query: str, context_results: List[Dict]) -> str:
        """Generate an enhanced prompt with context for legal questions"""
        if not context_results:
            return self._generate_legal_prompt_without_context(query)
        
        # Build context from retrieved documents
        context_parts = []
        for result in context_results:
            title = result['metadata'].get('title', 'Unknown Document')
            content = result['content']
            context_parts.append(f"Document: '{title}'\nContent: {content}")
        
        context = "\n\n".join(context_parts)
        
        # Create enhanced prompt for legal questions
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
        """Get RAG system statistics"""
        try:
            vector_stats = self.vector_store.get_stats()
            
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
                    'sources': sources
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
                    'sources': {}
                },
                'processor_config': {
                    'chunk_size': 1000,
                    'chunk_overlap': 200
                }
            }