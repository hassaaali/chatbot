from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import logging
import gc
import psutil
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
from services.huggingface_client import HuggingFaceClient

# Configure logging with more detail
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

app = FastAPI(title="Legal RAG-Enhanced PDF Chatbot API (Hugging Face)", version="1.0.0")

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
huggingface_client = None

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
    # Check system memory before initialization
    memory = psutil.virtual_memory()
    logger.info(f"System memory: {memory.percent}% used, {memory.available / (1024**3):.2f} GB available")
    
    if memory.percent > 70:
        logger.warning("High memory usage detected, using minimal configuration")
    
    # Initialize Hugging Face client
    logger.info("Initializing Hugging Face client...")
    huggingface_client = HuggingFaceClient()
    logger.info("Hugging Face client initialized")
    
    # Initialize document processor with optimized settings
    logger.info("Initializing document processor...")
    document_processor = DocumentProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    logger.info("Document processor initialized")
    
    # Initialize vector store with memory optimization
    logger.info("Initializing vector store...")
    vector_store = VectorStore(Config.CHROMA_DB_PATH, Config.EMBEDDING_MODEL)
    logger.info("Vector store initialized")
    
    # Initialize RAG service
    logger.info("Initializing RAG service...")
    rag_service = RAGService(vector_store, document_processor)
    logger.info("RAG service initialized")
    
    # Initialize file upload service with reduced file size limit
    logger.info("Initializing file upload service...")
    file_upload_service = FileUploadService(Config.MAX_FILE_SIZE)
    logger.info("File upload service initialized")
    
    logger.info("All services initialized successfully")
        
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")

# Pydantic models
class PromptRequest(BaseModel):
    prompt: str
    use_rag: bool = True
    model: Optional[str] = None

class DocumentResponse(BaseModel):
    success: bool
    message: str
    document_info: Optional[dict] = None

@app.get("/")
async def root():
    return {"message": "Legal RAG-Enhanced PDF Chatbot API (Hugging Face)", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    memory = psutil.virtual_memory()
    return {
        "status": "healthy",
        "model": Config.LLM_MODEL,
        "api_provider": "Hugging Face",
        "memory_usage_percent": memory.percent,
        "available_memory_gb": memory.available / (1024**3),
        "services": {
            "rag": rag_service is not None,
            "vector_store": vector_store is not None,
            "document_processor": document_processor is not None,
            "file_upload": file_upload_service is not None,
            "huggingface": huggingface_client is not None
        }
    }

@app.get("/models")
async def get_available_models():
    """Get list of available Hugging Face models for legal analysis"""
    if not huggingface_client:
        raise HTTPException(status_code=503, detail="Hugging Face client not available")
    
    return {
        "current_model": Config.LLM_MODEL,
        "available_models": huggingface_client.get_available_models(),
        "model_descriptions": {
            "microsoft/DialoGPT-medium": "Medium conversational model, good for legal Q&A (memory optimized)",
            "google/flan-t5-base": "Base instruction-following model, good for legal analysis",
            "facebook/blenderbot-400M-distill": "Balanced model for legal document discussion",
            "microsoft/GODEL-v1_1-base-seq2seq": "Goal-oriented model for legal guidance"
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
    """Upload a PDF file directly to the RAG system with detailed logging"""
    logger.info(f"=== STARTING PDF UPLOAD: {file.filename} ===")
    
    if not file_upload_service:
        raise HTTPException(status_code=503, detail="File upload service not available")
    
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        # Check memory before starting
        memory = psutil.virtual_memory()
        logger.info(f"Memory before upload: {memory.percent}% used, {memory.available / (1024**3):.2f} GB available")
        
        if memory.percent > 75:
            raise HTTPException(status_code=507, detail=f"Insufficient memory ({memory.percent}% used). Please try again later.")
        
        # Process the uploaded PDF with memory optimization
        logger.info("=== STEP 1: Processing uploaded PDF ===")
        document = await file_upload_service.process_uploaded_pdf(file, title)
        logger.info("=== STEP 1 COMPLETED: PDF processing completed ===")
        
        # Check memory after PDF processing
        memory_after_pdf = psutil.virtual_memory()
        logger.info(f"Memory after PDF processing: {memory_after_pdf.percent}% used")
        
        # Add to RAG system with detailed logging
        logger.info("=== STEP 2: Adding to RAG system ===")
        rag_service.add_document(document)
        logger.info("=== STEP 2 COMPLETED: Document added to RAG system successfully ===")
        
        # Force garbage collection after processing
        gc.collect()
        
        # Final memory check
        final_memory = psutil.virtual_memory()
        logger.info(f"Final memory usage: {final_memory.percent}% used")
        
        logger.info(f"=== UPLOAD COMPLETED SUCCESSFULLY: {file.filename} ===")
        
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
        logger.error(f"=== UPLOAD FAILED: {file.filename} - Error: {e} ===")
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
        stats["api_provider"] = "Hugging Face"
        stats["current_model"] = Config.LLM_MODEL
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
    model = prompt_request.model or Config.LLM_MODEL
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    if not huggingface_client:
        raise HTTPException(status_code=503, detail="Hugging Face client not available")

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
                enhanced_prompt = rag_service._generate_legal_prompt_without_context(prompt)
        except Exception as e:
            logger.warning(f"RAG enhancement failed, using legal prompt without context: {e}")
            enhanced_prompt = rag_service._generate_legal_prompt_without_context(prompt)

    async def event_generator():
        try:
            # Send context information first if available
            if context_info:
                yield f"data: [CONTEXT] Using legal information from: {', '.join(context_info['sources'])}\n\n"
            
            # Check if Hugging Face API key is available
            if not Config.HUGGINGFACE_API_KEY:
                yield f"data: [ERROR] Hugging Face API key not configured. Please set HUGGINGFACE_API_KEY in your environment.\n\n"
                return
            
            # Send model information
            yield f"data: [MODEL] Using Hugging Face model: {model}\n\n"
            
            # Stream response from Hugging Face
            async for chunk in huggingface_client.generate_text_stream(enhanced_prompt, model):
                if chunk.startswith("[ERROR]"):
                    yield f"data: {chunk}\n\n"
                    return
                
                if chunk.strip():
                    yield f"data: {chunk}\n\n"
                
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("Client disconnected, stopping stream")
                    break
                        
        except Exception as e:
            logger.error(f"Unexpected error in stream: {e}")
            yield f"data: [ERROR] Internal server error: {str(e)}\n\n"
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