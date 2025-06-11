import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json

from config import settings
from services.google_docs_service import GoogleDocsService
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.rag_service import RAGService

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
google_docs_service = GoogleDocsService()
document_processor = DocumentProcessor()
vector_store = VectorStore()
rag_service = RAGService(vector_store)

class DocumentRequest(BaseModel):
    document_id: str

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = False

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None

@app.post("/documents/add")
async def add_document(request: DocumentRequest):
    try:
        # Get document content from Google Docs
        doc_content = await google_docs_service.get_document(request.document_id)
        
        # Process document into chunks
        chunks = document_processor.process_document(doc_content, request.document_id)
        
        # Add to vector store
        vector_store.add_documents(chunks)
        
        return {"message": "Document added successfully", "document_id": request.document_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def remove_document(document_id: str):
    try:
        vector_store.remove_document(document_id)
        return {"message": "Document removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/stats")
async def get_stats():
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/clear")
async def clear_documents():
    try:
        vector_store.clear_all()
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        if request.use_rag:
            response_data = await rag_service.generate_response(request.message)
        else:
            # Simple chat without RAG
            response_data = {
                "response": f"Echo: {request.message}",
                "sources": []
            }
        
        def generate():
            yield f"data: {json.dumps(response_data)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)