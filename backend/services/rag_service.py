import together
from typing import List, Dict
from config import settings
from .vector_store import VectorStore

class RAGService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        together.api_key = settings.together_api_key
    
    async def generate_response(self, query: str) -> Dict:
        """Generate response using RAG pipeline"""
        # Retrieve relevant documents
        relevant_docs = self.vector_store.search(query)
        
        if not relevant_docs:
            return {
                "response": "I don't have enough information to answer that question based on the available documents.",
                "sources": []
            }
        
        # Build context from retrieved documents
        context = self._build_context(relevant_docs)
        
        # Generate response using Together AI
        response = await self._generate_with_context(query, context)
        
        # Extract sources
        sources = list(set([doc['metadata']['source'] for doc in relevant_docs]))
        
        return {
            "response": response,
            "sources": sources
        }
    
    def _build_context(self, documents: List[Dict]) -> str:
        """Build context string from retrieved documents"""
        context_parts = []
        
        for doc in documents:
            title = doc['metadata'].get('title', 'Unknown Document')
            content = doc['content']
            context_parts.append(f"From '{title}':\n{content}")
        
        return "\n\n".join(context_parts)
    
    async def _generate_with_context(self, query: str, context: str) -> str:
        """Generate response using Together AI with context"""
        prompt = f"""Based on the following context, please answer the question. If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            response = together.Complete.create(
                prompt=prompt,
                model="togethercomputer/llama-2-70b-chat",
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["</s>", "[INST]", "[/INST]"]
            )
            
            return response['output']['choices'][0]['text'].strip()
        except Exception as e:
            return f"I encountered an error while generating the response: {str(e)}"