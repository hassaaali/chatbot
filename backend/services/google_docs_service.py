from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GoogleDocsService:
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Docs API"""
        creds = None
        token_path = 'token.json'
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Google credentials file not found: {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('docs', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Google Docs API")
    
    def get_document_content(self, document_id: str) -> Dict:
        """Retrieve content from a Google Doc"""
        try:
            document = self.service.documents().get(documentId=document_id).execute()
            return self._extract_text_from_document(document)
        except HttpError as error:
            logger.error(f"Error retrieving document {document_id}: {error}")
            raise
    
    def _extract_text_from_document(self, document: Dict) -> Dict:
        """Extract text content from Google Docs document structure"""
        content = document.get('body', {}).get('content', [])
        text_content = []
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                paragraph_text = ""
                
                for text_element in paragraph.get('elements', []):
                    if 'textRun' in text_element:
                        paragraph_text += text_element['textRun'].get('content', '')
                
                if paragraph_text.strip():
                    text_content.append(paragraph_text.strip())
        
        return {
            'title': document.get('title', 'Untitled Document'),
            'document_id': document.get('documentId'),
            'content': '\n'.join(text_content),
            'revision_id': document.get('revisionId')
        }
    
    def list_documents_from_drive(self, max_results: int = 10) -> List[Dict]:
        """List Google Docs from Drive (requires Drive API scope)"""
        # This would require additional Drive API setup
        # For now, users will provide document IDs directly
        pass