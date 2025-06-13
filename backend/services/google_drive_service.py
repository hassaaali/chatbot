import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GoogleDriveService:
    # Updated scopes - make sure both are included
    SCOPES = [
        'https://www.googleapis.com/auth/documents.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.drive_service = None
        self.docs_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs"""
        creds = None
        token_path = 'token.pickle'
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed existing credentials")
                except Exception as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    # Delete the old token and re-authenticate
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    creds = None
            
            if not creds:
                logger.info("Starting new OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                # Use run_local_server with specific parameters for better compatibility
                creds = flow.run_local_server(
                    port=0,
                    prompt='consent',
                    authorization_prompt_message='Please visit this URL to authorize the application: {url}',
                    success_message='The auth flow is complete; you may close this window.',
                    open_browser=True
                )
                logger.info("OAuth flow completed successfully")
            
            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
                logger.info("Saved new credentials")
        
        # Verify scopes
        if hasattr(creds, 'scopes'):
            logger.info(f"Current scopes: {creds.scopes}")
            required_scopes = set(self.SCOPES)
            current_scopes = set(creds.scopes) if creds.scopes else set()
            
            if not required_scopes.issubset(current_scopes):
                logger.warning("Insufficient scopes detected. Re-authenticating...")
                # Delete token and re-authenticate with correct scopes
                if os.path.exists(token_path):
                    os.remove(token_path)
                return self._authenticate()
        
        try:
            self.drive_service = build('drive', 'v3', credentials=creds)
            self.docs_service = build('docs', 'v1', credentials=creds)
            logger.info("Google Drive and Docs services authenticated successfully")
            
            # Test the connection
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to build services: {e}")
            # If building services fails, delete token and retry
            if os.path.exists(token_path):
                os.remove(token_path)
                logger.info("Deleted invalid token, please restart the application")
            raise Exception("Authentication failed. Please restart the application to re-authenticate.")
    
    def _test_connection(self):
        """Test the API connection with a simple request"""
        try:
            # Test Drive API with a minimal request
            result = self.drive_service.files().list(
                pageSize=1,
                fields="files(id, name)"
            ).execute()
            logger.info("Drive API connection test successful")
            
            # Test if we can access documents specifically
            doc_result = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.document'",
                pageSize=1,
                fields="files(id, name)"
            ).execute()
            logger.info("Document access test successful")
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.error("Insufficient permissions. Please re-authenticate with proper scopes.")
                raise Exception("Insufficient permissions. Please delete token.pickle and restart the application.")
            else:
                logger.error(f"API test failed: {e}")
                raise
    
    def scan_folder(self, folder_id: Optional[str] = None, include_subfolders: bool = True) -> List[Dict]:
        """
        Scan a Google Drive folder for documents
        If folder_id is None, scans the entire Drive
        """
        try:
            documents = []
            
            # Build query
            query = "mimeType='application/vnd.google-apps.document'"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            logger.info(f"Scanning with query: {query}")
            
            # Get all Google Docs in the folder
            results = self.drive_service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, parents, modifiedTime, webViewLink)",
                pageSize=1000
            ).execute()
            
            items = results.get('files', [])
            logger.info(f"Found {len(items)} documents")
            
            for item in items:
                doc_info = {
                    'id': item['id'],
                    'title': item['name'],
                    'modified_time': item.get('modifiedTime'),
                    'url': item.get('webViewLink', f"https://docs.google.com/document/d/{item['id']}/edit"),
                    'parents': item.get('parents', [])
                }
                documents.append(doc_info)
            
            # If include_subfolders, recursively scan subfolders
            if include_subfolders and folder_id:
                subfolders = self._get_subfolders(folder_id)
                for subfolder in subfolders:
                    subdocs = self.scan_folder(subfolder['id'], include_subfolders=True)
                    documents.extend(subdocs)
            
            logger.info(f"Total documents found: {len(documents)}")
            return documents
            
        except HttpError as error:
            logger.error(f'Google Drive API error: {error}')
            if error.resp.status == 403:
                raise Exception('Insufficient permissions. Please delete token.pickle and restart the application to re-authenticate with proper scopes.')
            raise Exception(f'Failed to scan Drive folder: {error}')
        except Exception as error:
            logger.error(f'Unexpected error scanning folder: {error}')
            raise Exception(f'Failed to scan Drive folder: {error}')
    
    def _get_subfolders(self, folder_id: str) -> List[Dict]:
        """Get all subfolders within a folder"""
        try:
            query = f"mimeType='application/vnd.google-apps.folder' and '{folder_id}' in parents"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as error:
            logger.error(f'Error getting subfolders: {error}')
            return []
    
    def get_document_content(self, document_id: str) -> Dict:
        """Get the content of a specific document"""
        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            
            title = document.get('title', 'Untitled')
            content = self._extract_text_from_document(document)
            
            return {
                'id': document_id,
                'title': title,
                'content': content,
                'url': f'https://docs.google.com/document/d/{document_id}/edit'
            }
        except HttpError as error:
            logger.error(f'Google Docs API error: {error}')
            raise Exception(f'Failed to retrieve document: {error}')
        except Exception as error:
            logger.error(f'Unexpected error retrieving document: {error}')
            raise Exception(f'Failed to retrieve document: {error}')
    
    def _extract_text_from_document(self, document):
        """Extract plain text from Google Docs document structure"""
        text = ''
        content = document.get('body', {}).get('content', [])
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_element in paragraph.get('elements', []):
                    if 'textRun' in text_element:
                        text += text_element['textRun']['content']
            elif 'table' in element:
                # Handle tables
                table = element['table']
                for row in table.get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        for cell_element in cell.get('content', []):
                            if 'paragraph' in cell_element:
                                paragraph = cell_element['paragraph']
                                for text_element in paragraph.get('elements', []):
                                    if 'textRun' in text_element:
                                        text += text_element['textRun']['content']
                        text += '\t'  # Add tab between cells
                    text += '\n'  # Add newline between rows
        
        return text.strip()
    
    def get_folder_info(self, folder_id: str) -> Dict:
        """Get information about a specific folder"""
        try:
            folder = self.drive_service.files().get(
                fileId=folder_id,
                fields="id, name, parents, webViewLink"
            ).execute()
            
            return {
                'id': folder['id'],
                'name': folder['name'],
                'url': folder.get('webViewLink', ''),
                'parents': folder.get('parents', [])
            }
            
        except Exception as error:
            logger.error(f'Error getting folder info: {error}')
            raise Exception(f'Failed to get folder info: {error}')
    
    def search_documents(self, query: str, folder_id: Optional[str] = None) -> List[Dict]:
        """Search for documents by name or content"""
        try:
            search_query = f"mimeType='application/vnd.google-apps.document' and fullText contains '{query}'"
            if folder_id:
                search_query += f" and '{folder_id}' in parents"
            
            results = self.drive_service.files().list(
                q=search_query,
                fields="files(id, name, webViewLink)",
                pageSize=100
            ).execute()
            
            items = results.get('files', [])
            documents = []
            
            for item in items:
                doc_info = {
                    'id': item['id'],
                    'title': item['name'],
                    'url': item.get('webViewLink', f"https://docs.google.com/document/d/{item['id']}/edit")
                }
                documents.append(doc_info)
            
            return documents
            
        except Exception as error:
            logger.error(f'Error searching documents: {error}')
            return []