import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            raise Exception(f'An error occurred: {error}')
    
    def _extract_text_from_document(self, document):
        text = ''
        content = document.get('body', {}).get('content', [])
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_element in paragraph.get('elements', []):
                    if 'textRun' in text_element:
                        text += text_element['textRun']['content']
        
        return text