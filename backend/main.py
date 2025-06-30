from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import json
import logging
import gc
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncio
import signal
import sys
import atexit
import shutil

from config import Config
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.rag_service import RAGService
from services.file_upload_service import FileUploadService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except Exception as e:
    logger.warning(f"Configuration validation failed: {e}")

app = FastAPI(title="Legal RAG-Enhanced PDF Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize core services
document_processor = None
vector_store = None
rag_service = None
file_upload_service = None

def cleanup_cache():
    """Clean up cache and temporary files on application shutdown"""
    try:
        logger.info("Starting application cleanup...")
        
        # Clear vector store if available
        if rag_service:
            try:
                rag_service.clear_all_documents()
                logger.info("Cleared all documents from RAG system")
            except Exception as e:
                logger.warning(f"Error clearing RAG documents: {e}")
        
        # Remove ChromaDB directory
        if os.path.exists(Config.CHROMA_DB_PATH):
            try:
                shutil.rmtree(Config.CHROMA_DB_PATH)
                logger.info(f"Removed ChromaDB directory: {Config.CHROMA_DB_PATH}")
            except Exception as e:
                logger.warning(f"Error removing ChromaDB directory: {e}")
        
        # Clean up any temporary files
        temp_dirs = ['./temp', './tmp', './uploads']
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Removed temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Error removing temp directory {temp_dir}: {e}")
        
        # Clean up any .pickle files (authentication tokens)
        pickle_files = ['token.pickle', 'drive_sync_state.json']
        for pickle_file in pickle_files:
            if os.path.exists(pickle_file):
                try:
                    os.remove(pickle_file)
                    logger.info(f"Removed file: {pickle_file}")
                except Exception as e:
                    logger.warning(f"Error removing file {pickle_file}: {e}")
        
        # Force garbage collection
        gc.collect()
        
        logger.info("Application cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    cleanup_cache()
    sys.exit(0)

# Register cleanup functions
atexit.register(cleanup_cache)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    # Initialize document processor with optimized settings
    document_processor = DocumentProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    logger.info("Document processor initialized")
    
    # Initialize vector store with memory optimization
    vector_store = VectorStore(Config.CHROMA_DB_PATH, Config.EMBEDDING_MODEL)
    logger.info("Vector store initialized")
    
    # Initialize RAG service
    rag_service = RAGService(vector_store, document_processor)
    logger.info("RAG service initialized")
    
    # Initialize file upload service with reduced file size limit
    file_upload_service = FileUploadService(Config.MAX_FILE_SIZE)
    logger.info("File upload service initialized")
    
    logger.info("All services initialized successfully")
        
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")

# Pydantic models
class PromptRequest(BaseModel):
    prompt: str
    use_rag: bool = True

class DocumentResponse(BaseModel):
    success: bool
    message: str
    document_info: Optional[dict] = None

@app.get("/")
async def root():
    return {"message": "Legal RAG-Enhanced PDF Chatbot API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": Config.LLM_MODEL,
        "services": {
            "rag": rag_service is not None,
            "vector_store": vector_store is not None,
            "document_processor": document_processor is not None,
            "file_upload": file_upload_service is not None
        }
    }

@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI shutdown event handler"""
    logger.info("FastAPI shutdown event triggered")
    cleanup_cache()

# File upload endpoints
@app.post("/documents/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None)
) -> DocumentResponse:
    """Upload a PDF file directly to the RAG system"""
    logger.info(f"Received file upload request: {file.filename}")
    
    if not file_upload_service:
        raise HTTPException(status_code=503, detail="File upload service not available")
    
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        # Process the uploaded PDF with memory optimization
        logger.info("Processing uploaded PDF...")
        document = await file_upload_service.process_uploaded_pdf(file, title)
        logger.info("PDF processing completed, adding to RAG system...")
        
        # Add to RAG system
        rag_service.add_document(document)
        logger.info("Document added to RAG system successfully")
        
        # Force garbage collection after processing
        gc.collect()
        
        return DocumentResponse(
            success=True,
            message=f"Successfully uploaded and processed legal document '{document['title']}'",
            document_info={
                "title": document['title'],
                "document_id": document['id'],
                "content_length": len(document['content']),
                "file_size": document.get('size', 0),
                "filename": document.get('filename', ''),
                "source": "upload"
            }
        )
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        # Force garbage collection on error
        gc.collect()
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Remove a document from the RAG system"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        rag_service.delete_document(document_id)
        gc.collect()  # Force garbage collection after deletion
        return {"success": True, "message": f"Document {document_id} removed successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/documents/stats")
async def get_system_stats():
    """Get RAG system statistics"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        stats = rag_service.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.delete("/documents/clear")
async def clear_all_documents():
    """Clear all documents from the RAG system"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        rag_service.clear_all_documents()
        gc.collect()  # Force garbage collection after clearing
        return {"success": True, "message": "All documents cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear documents: {str(e)}")

@app.post("/chat/stream")
async def stream_chat(prompt_request: PromptRequest, request: Request):
    prompt = prompt_request.prompt.strip()
    use_rag = prompt_request.use_rag
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # Enhance prompt with RAG if enabled and available
    enhanced_prompt = prompt
    context_info = None
    
    if use_rag and rag_service:
        try:
            # Retrieve relevant context
            context_results = rag_service.retrieve_context(prompt, Config.MAX_RETRIEVAL_RESULTS)
            
            if context_results:
                enhanced_prompt = rag_service.generate_rag_prompt(prompt, context_results)
                context_info = {
                    "retrieved_contexts": len(context_results),
                    "sources": list(set([
                        result['metadata'].get('title', 'Unknown') 
                        for result in context_results
                    ]))
                }
                logger.info(f"Enhanced legal prompt with {len(context_results)} context results")
            else:
                # Use legal-specific prompt even without context
                enhanced_prompt = rag_service.generate_rag_prompt(prompt, [])
        except Exception as e:
            logger.warning(f"RAG enhancement failed, using legal prompt without context: {e}")
            enhanced_prompt = rag_service._generate_legal_prompt_without_context(prompt)

    async def event_generator():
        buffer = ""
        try:
            # Send context information first if available
            if context_info:
                yield f"data: [CONTEXT] Using legal information from: {', '.join(context_info['sources'])}\n\n"
            
            # Check if Together API key is available
            if not Config.TOGETHER_API_KEY:
                yield f"data: [ERROR] Together AI API key not configured. Please set TOGETHER_API_KEY in your environment.\n\n"
                return
            
            async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout
                async with client.stream(
                    "POST",
                    "https://api.together.xyz/inference",
                    headers={"Authorization": f"Bearer {Config.TOGETHER_API_KEY}"},
                    json={
                        "model": Config.LLM_MODEL,
                        "prompt": enhanced_prompt,
                        "stream": True,
                        "max_tokens": Config.LLM_MAX_TOKENS,
                        "temperature": Config.LLM_TEMPERATURE,
                        "top_p": Config.LLM_TOP_P
                    }
                ) as response:
                    if response.status_code != 200:
                        logger.error(f"Together API error: {response.status_code}")
                        error_text = await response.atext()
                        logger.error(f"Error details: {error_text}")
                        yield f"data: [ERROR] API Error: {response.status_code}\n\n"
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            content = line[5:].strip()
                            if content and content != "[DONE]":
                                try:
                                    data = json.loads(content)
                                    choices = data.get("choices", [])
                                    if choices:
                                        text = choices[0].get("text", "")
                                        if text:
                                            buffer += text
                                            # Split buffer by meaningful separators
                                            lines = buffer.split("\n")
                                            buffer = lines[-1]
                                            for line in lines[:-1]:
                                                if line.strip():
                                                    yield f"data: {line.strip()}\n\n"
                                except Exception as e:
                                    logger.warning(f"Could not parse chunk: {content} ({e})")
                        
                        if await request.is_disconnected():
                            logger.info("Client disconnected, stopping stream")
                            break
                    
                    # Yield any remaining buffer content
                    if buffer.strip():
                        yield f"data: {buffer.strip()}\n\n"
                        
        except httpx.RequestError as e:
            logger.error(f"Network error: {e}")
            yield f"data: [ERROR] Network error occurred\n\n"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            yield f"data: [ERROR] Internal server error\n\n"
        finally:
            # Force garbage collection after streaming
            gc.collect()

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        cleanup_cache()
    except Exception as e:
        logger.error(f"Server error: {e}")
        cleanup_cache()
        raise