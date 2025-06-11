import together
from typing import AsyncGenerator, Dict, List, Optional
import asyncio
import json
from config import Config

class RAGService:
    def __init__(self, vector_store, max_retrieval_results: int = 5):
        self.vector_store = vector_store
        self.max_retrieval_results = max_retrieval_results
        self.config = Config()
        
        # Initialize Together client
        together.api_key = self.config.TOGETHER_API_KEY
    
    async def chat_with_rag(self, query: str) -> AsyncGenerator[Dict, None]:
        """Chat with RAG enhancement"""
        # Retrieve relevant documents
        relevant_docs = self.vector_store.search(query, self.max_retrieval_results)
        
        # Build context from retrieved documents
        context = self._build_context(relevant_docs)
        
        # Create enhanced prompt
        enhanced_prompt = self._create_rag_prompt(query, context)
        
        # Get sources for attribution
        sources = self._extract_sources(relevant_docs)
        
        # Stream response
        async for chunk in self._stream_response(enhanced_prompt):
            chunk['sources'] = sources
            yield chunk
    
    async def chat_without_rag(self, query: str) -> AsyncGenerator[Dict, None]:
        """Chat without RAG enhancement"""
        prompt = f"User: {query}\nAssistant:"
        
        async for chunk in self._stream_response(prompt):
            yield chunk
    
    def _build_context(self, relevant_docs: List[Dict]) -> str:
        """Build context string from relevant documents"""
        if not relevant_docs:
            return ""
        
        context_parts = []
        for doc in relevant_docs:
            title = doc['metadata'].get('title', 'Unknown Document')
            content = doc['content']
            context_parts.append(f"From '{title}':\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create enhanced prompt with context"""
        if not context:
            return f"User: {query}\nAssistant:"
        
        prompt = f"""You are a helpful assistant. Use the following context to answer the user's question. If the context doesn't contain relevant information, say so clearly.

Context:
{context}

User: {query}
Assistant:"""
        
        return prompt
    
    def _extract_sources(self, relevant_docs: List[Dict]) -> List[str]:
        """Extract unique sources from relevant documents"""
        sources = set()
        for doc in relevant_docs:
            metadata = doc['metadata']
            title = metadata.get('title', 'Unknown Document')
            url = metadata.get('url', '')
            if url:
                sources.add(f"{title} ({url})")
            else:
                sources.add(title)
        
        return list(sources)
    
    async def _stream_response(self, prompt: str) -> AsyncGenerator[Dict, None]:
        """Stream response from Together API"""
        try:
            response = together.Complete.create(
                prompt=prompt,
                model="meta-llama/Llama-2-7b-chat-hf",
                max_tokens=512,
                temperature=0.7,
                stream=True
            )
            
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    content = chunk['choices'][0].get('text', '')
                    if content:
                        yield {
                            'type': 'content',
                            'content': content
                        }
            
            yield {
                'type': 'done'
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'content': f'Error: {str(e)}'
            }