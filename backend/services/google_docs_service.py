import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleDocsService:
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.service = self._authenticate()
    
    def _authenticate(self):
        creds = None
        token_path = 'token.pickle'
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('docs', 'v1', credentials=creds)
    
    def get_document_content(self, document_id):
        """Retrieve document content from Google Docs"""
        try:
            document = self.service.documents().get(documentId=document_id).execute()
            
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