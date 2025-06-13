from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import json
import logging
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncio

from config import Config
from services.google_docs_service import GoogleDocsService
from services.google_drive_service import GoogleDriveService
from services.drive_sync_service import DriveSyncService
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except Exception as e:
    logger.warning(f"Configuration validation failed: {e}")

app = FastAPI(title="RAG-Enhanced Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize services
google_docs_service = None
google_drive_service = None
drive_sync_service = None
document_processor = None
vector_store = None
rag_service = None

try:
    # Initialize document processor
    document_processor = DocumentProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    logger.info("Document processor initialized")
    
    # Initialize vector store
    vector_store = VectorStore(Config.CHROMA_DB_PATH, Config.EMBEDDING_MODEL)
    logger.info("Vector store initialized")
    
    # Initialize RAG service
    rag_service = RAGService(vector_store, document_processor)
    logger.info("RAG service initialized")
    
    # Initialize Google services (optional)
    if os.path.exists(Config.GOOGLE_CREDENTIALS_PATH):
        google_docs_service = GoogleDocsService(Config.GOOGLE_CREDENTIALS_PATH)
        google_drive_service = GoogleDriveService(Config.GOOGLE_CREDENTIALS_PATH)
        drive_sync_service = DriveSyncService(google_drive_service, rag_service)
        logger.info("Google services initialized")
    else:
        logger.warning(f"Google credentials file not found at {Config.GOOGLE_CREDENTIALS_PATH}")
        
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")

# Pydantic models
class PromptRequest(BaseModel):
    prompt: str
    use_rag: bool = True

class DocumentRequest(BaseModel):
    document_id: str
    title: Optional[str] = None

class FolderSyncRequest(BaseModel):
    folder_id: Optional[str] = None
    force_full_sync: bool = False

class DocumentResponse(BaseModel):
    success: bool
    message: str
    document_info: Optional[dict] = None

class SyncResponse(BaseModel):
    success: bool
    message: str
    stats: Optional[dict] = None

@app.get("/")
async def root():
    return {"message": "RAG-Enhanced Chatbot API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "google_docs": google_docs_service is not None,
            "google_drive": google_drive_service is not None,
            "drive_sync": drive_sync_service is not None,
            "rag": rag_service is not None,
            "vector_store": vector_store is not None,
            "document_processor": document_processor is not None
        }
    }

# Individual document management (existing functionality)
@app.post("/documents/add")
async def add_document(request: DocumentRequest) -> DocumentResponse:
    """Add a single Google Doc to the RAG system"""
    if not google_docs_service:
        raise HTTPException(
            status_code=503, 
            detail="Google Docs service not available. Please ensure credentials.json is configured."
        )
    
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        # Retrieve document from Google Docs
        document = google_docs_service.get_document_content(request.document_id)
        
        # Override title if provided
        if request.title:
            document['title'] = request.title
        
        # Add to RAG system
        rag_service.add_document(document)
        
        return DocumentResponse(
            success=True,
            message=f"Successfully added document '{document['title']}'",
            document_info={
                "title": document['title'],
                "document_id": document['id'],
                "content_length": len(document['content'])
            }
        )
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

# New Drive folder management endpoints
@app.post("/drive/sync")
async def sync_drive_folder(request: FolderSyncRequest, background_tasks: BackgroundTasks) -> SyncResponse:
    """Sync documents from a Google Drive folder"""
    if not drive_sync_service:
        raise HTTPException(
            status_code=503,
            detail="Google Drive service not available. Please ensure credentials.json is configured."
        )
    
    try:
        # Run sync in background for large folders
        if request.force_full_sync:
            background_tasks.add_task(
                drive_sync_service.sync_folder,
                request.folder_id,
                request.force_full_sync
            )
            return SyncResponse(
                success=True,
                message="Full sync started in background. Check /drive/sync/status for progress."
            )
        else:
            # Quick sync in foreground
            stats = await drive_sync_service.sync_folder(request.folder_id, request.force_full_sync)
            return SyncResponse(
                success=True,
                message=f"Sync completed: {stats['added']} added, {stats['updated']} updated, {stats['errors']} errors",
                stats=stats
            )
    except Exception as e:
        logger.error(f"Error syncing Drive folder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync folder: {str(e)}")

@app.get("/drive/sync/status")
async def get_sync_status():
    """Get current sync status"""
    if not drive_sync_service:
        raise HTTPException(status_code=503, detail="Drive sync service not available")
    
    return drive_sync_service.get_sync_status()

@app.post("/drive/scan")
async def scan_drive_folder(folder_id: Optional[str] = None):
    """Scan a Drive folder without syncing (preview what would be synced)"""
    if not google_drive_service:
        raise HTTPException(status_code=503, detail="Google Drive service not available")
    
    try:
        documents = google_drive_service.scan_folder(folder_id, include_subfolders=True)
        return {
            "folder_id": folder_id,
            "total_documents": len(documents),
            "documents": [
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "url": doc["url"],
                    "modified_time": doc.get("modified_time")
                }
                for doc in documents[:50]  # Limit to first 50 for preview
            ],
            "showing_first": min(50, len(documents))
        }
    except Exception as e:
        logger.error(f"Error scanning Drive folder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan folder: {str(e)}")

@app.post("/drive/auto-sync")
async def trigger_auto_sync(folder_id: Optional[str] = None):
    """Trigger auto-sync if needed"""
    if not drive_sync_service:
        raise HTTPException(status_code=503, detail="Drive sync service not available")
    
    try:
        stats = await drive_sync_service.auto_sync_if_needed(folder_id)
        if stats:
            return SyncResponse(
                success=True,
                message="Auto-sync completed",
                stats=stats
            )
        else:
            return SyncResponse(
                success=True,
                message="No sync needed at this time"
            )
    except Exception as e:
        logger.error(f"Error in auto-sync: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-sync failed: {str(e)}")

# Existing endpoints (unchanged)
@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Remove a document from the RAG system"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        rag_service.delete_document(document_id)
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
        
        # Add sync status if available
        if drive_sync_service:
            stats['sync_status'] = drive_sync_service.get_sync_status()
        
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
        
        # Also clear sync state if available
        if drive_sync_service:
            drive_sync_service.clear_sync_state()
        
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

    # Auto-sync if needed (non-blocking)
    if drive_sync_service:
        try:
            asyncio.create_task(drive_sync_service.auto_sync_if_needed())
        except:
            pass  # Don't fail chat if auto-sync fails

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
                logger.info(f"Enhanced prompt with {len(context_results)} context results")
        except Exception as e:
            logger.warning(f"RAG enhancement failed, using original prompt: {e}")

    async def event_generator():
        buffer = ""
        try:
            # Send context information first if available
            if context_info:
                yield f"data: [CONTEXT] Using information from: {', '.join(context_info['sources'])}\n\n"
            
            # Check if Together API key is available
            if not Config.TOGETHER_API_KEY:
                yield f"data: [ERROR] Together AI API key not configured. Please set TOGETHER_API_KEY in your environment.\n\n"
                return
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.together.xyz/inference",
                    headers={"Authorization": f"Bearer {Config.TOGETHER_API_KEY}"},
                    json={
                        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                        "prompt": enhanced_prompt,
                        "stream": True,
                        "max_tokens": 4000,
                        "temperature": 0.1,
                        "top_p": 0.9
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

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)