from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
from typing import Optional, List
import asyncio

from services.google_docs_service import GoogleDocsService
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.rag_service import RAGService
from config import Config

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
config = Config()
google_docs_service = GoogleDocsService(config.GOOGLE_CREDENTIALS_PATH)
document_processor = DocumentProcessor(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
vector_store = VectorStore(config.CHROMA_DB_PATH, config.EMBEDDING_MODEL)
rag_service = RAGService(vector_store, config.MAX_RETRIEVAL_RESULTS)

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
        doc_content = google_docs_service.get_document_content(request.document_id)
        
        # Process document into chunks
        chunks = document_processor.process_document(doc_content, request.document_id)
        
        # Add to vector store
        vector_store.add_documents(chunks)
        
        return {"message": f"Document {request.document_id} added successfully", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def remove_document(document_id: str):
    try:
        vector_store.remove_document(document_id)
        return {"message": f"Document {document_id} removed successfully"}
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
            response_generator = rag_service.chat_with_rag(request.message)
        else:
            response_generator = rag_service.chat_without_rag(request.message)
        
        async def generate():
            async for chunk in response_generator:
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)