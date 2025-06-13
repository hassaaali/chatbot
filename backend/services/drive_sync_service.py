import asyncio
from typing import List, Dict, Optional, Set
import logging
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class DriveSyncService:
    def __init__(self, drive_service, rag_service, sync_interval_hours: int = 24):
        self.drive_service = drive_service
        self.rag_service = rag_service
        self.sync_interval_hours = sync_interval_hours
        self.sync_state_file = 'drive_sync_state.json'
        self.last_sync_time = None
        self.synced_documents = set()
        self._load_sync_state()
    
    def _load_sync_state(self):
        """Load sync state from file"""
        try:
            if os.path.exists(self.sync_state_file):
                with open(self.sync_state_file, 'r') as f:
                    state = json.load(f)
                    self.last_sync_time = datetime.fromisoformat(state.get('last_sync_time', '')) if state.get('last_sync_time') else None
                    self.synced_documents = set(state.get('synced_documents', []))
                    logger.info(f"Loaded sync state: {len(self.synced_documents)} documents, last sync: {self.last_sync_time}")
        except Exception as e:
            logger.warning(f"Could not load sync state: {e}")
            self.last_sync_time = None
            self.synced_documents = set()
    
    def _save_sync_state(self):
        """Save sync state to file"""
        try:
            state = {
                'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
                'synced_documents': list(self.synced_documents)
            }
            with open(self.sync_state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save sync state: {e}")
    
    async def sync_folder(self, folder_id: Optional[str] = None, force_full_sync: bool = False) -> Dict:
        """
        Sync documents from a Google Drive folder
        Returns sync statistics
        """
        try:
            logger.info(f"Starting Drive sync for folder: {folder_id or 'entire Drive'}")
            
            # Get all documents in the folder
            try:
                drive_documents = self.drive_service.scan_folder(folder_id, include_subfolders=True)
                logger.info(f"Successfully scanned folder, found {len(drive_documents)} documents")
            except Exception as e:
                logger.error(f"Failed to scan folder: {e}")
                raise Exception(f"Failed to scan Drive folder: {e}")
            
            stats = {
                'total_found': len(drive_documents),
                'added': 0,
                'updated': 0,
                'skipped': 0,
                'errors': 0,
                'error_details': []
            }
            
            if not drive_documents:
                logger.warning("No documents found in the specified folder")
                return stats
            
            for i, doc_info in enumerate(drive_documents):
                try:
                    doc_id = doc_info['id']
                    logger.info(f"Processing document {i+1}/{len(drive_documents)}: {doc_info.get('title', doc_id)}")
                    
                    # Check if document needs syncing
                    if not force_full_sync and doc_id in self.synced_documents:
                        # Check modification time if available
                        if doc_info.get('modified_time'):
                            try:
                                modified_time = datetime.fromisoformat(doc_info['modified_time'].replace('Z', '+00:00'))
                                if self.last_sync_time and modified_time <= self.last_sync_time:
                                    stats['skipped'] += 1
                                    logger.info(f"Skipping unchanged document: {doc_info.get('title', doc_id)}")
                                    continue
                            except Exception as e:
                                logger.warning(f"Could not parse modification time for {doc_id}: {e}")
                    
                    # Get document content
                    try:
                        document = self.drive_service.get_document_content(doc_id)
                        logger.info(f"Retrieved content for: {document['title']} ({len(document['content'])} chars)")
                    except Exception as e:
                        stats['errors'] += 1
                        error_msg = f"Error retrieving document {doc_info.get('title', doc_id)}: {str(e)}"
                        stats['error_details'].append(error_msg)
                        logger.error(error_msg)
                        continue
                    
                    # Check if document already exists in RAG system
                    is_update = doc_id in self.synced_documents
                    
                    # Add/update document in RAG system
                    if is_update:
                        # Remove old version first
                        try:
                            self.rag_service.delete_document(doc_id)
                            logger.info(f"Removed old version of: {document['title']}")
                        except Exception as e:
                            logger.warning(f"Could not remove old version of {doc_id}: {e}")
                    
                    # Add document to RAG system
                    try:
                        self.rag_service.add_document(document)
                        self.synced_documents.add(doc_id)
                        
                        if is_update:
                            stats['updated'] += 1
                            logger.info(f"Updated document: {document['title']}")
                        else:
                            stats['added'] += 1
                            logger.info(f"Added document: {document['title']}")
                    except Exception as e:
                        stats['errors'] += 1
                        error_msg = f"Error adding document {document['title']} to RAG system: {str(e)}"
                        stats['error_details'].append(error_msg)
                        logger.error(error_msg)
                        continue
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    stats['errors'] += 1
                    error_msg = f"Error processing document {doc_info.get('title', doc_info['id'])}: {str(e)}"
                    stats['error_details'].append(error_msg)
                    logger.error(error_msg)
            
            # Update sync time
            self.last_sync_time = datetime.now()
            self._save_sync_state()
            
            logger.info(f"Drive sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Drive sync failed: {e}")
            raise Exception(f"Drive sync failed: {e}")
    
    def should_sync(self) -> bool:
        """Check if it's time for a sync"""
        if not self.last_sync_time:
            return True
        
        time_since_sync = datetime.now() - self.last_sync_time
        return time_since_sync >= timedelta(hours=self.sync_interval_hours)
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        return {
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'synced_documents_count': len(self.synced_documents),
            'sync_interval_hours': self.sync_interval_hours,
            'should_sync': self.should_sync()
        }
    
    async def auto_sync_if_needed(self, folder_id: Optional[str] = None) -> Optional[Dict]:
        """Automatically sync if needed"""
        if self.should_sync():
            logger.info("Auto-sync triggered")
            return await self.sync_folder(folder_id)
        return None
    
    def clear_sync_state(self):
        """Clear sync state (useful for testing or reset)"""
        self.last_sync_time = None
        self.synced_documents.clear()
        if os.path.exists(self.sync_state_file):
            os.remove(self.sync_state_file)
        logger.info("Sync state cleared")