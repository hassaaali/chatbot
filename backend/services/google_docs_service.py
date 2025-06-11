import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import settings

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

class GoogleDocsService:
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Docs API"""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(settings.google_credentials_path):
                    raise FileNotFoundError(f"Google credentials file not found: {settings.google_credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.google_credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('docs', 'v1', credentials=creds)
    
    async def get_document(self, document_id: str) -> dict:
        """Retrieve document content from Google Docs"""
        try:
            document = self.service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = self._extract_text(document)
            
            return {
                'id': document_id,
                'title': document.get('title', 'Untitled'),
                'content': content,
                'metadata': {
                    'document_id': document_id,
                    'title': document.get('title', 'Untitled'),
                    'revision_id': document.get('revisionId', ''),
                }
            }
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def _extract_text(self, document: dict) -> str:
        """Extract plain text from Google Docs document structure"""
        text = ""
        content = document.get('body', {}).get('content', [])
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_element in paragraph.get('elements', []):
                    if 'textRun' in text_element:
                        text += text_element['textRun']['content']
        
        return text