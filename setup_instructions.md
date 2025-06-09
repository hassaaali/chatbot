# RAG-Enhanced Chatbot Setup Instructions

## Overview
This setup creates a comprehensive RAG (Retrieval-Augmented Generation) pipeline that integrates with Google Docs, allowing your chatbot to provide answers based on your document content.

## Prerequisites
1. Python 3.8+
2. Node.js 14+
3. Google Cloud Console account
4. Together AI API key

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Google Docs API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Docs API
4. Create credentials (OAuth 2.0 Client ID for desktop application)
5. Download the credentials JSON file and save as `backend/credentials.json`

### 3. Environment Configuration
1. Copy `backend/.env.example` to `backend/.env`
2. Fill in your API keys:
```env
TOGETHER_API_KEY=your_together_api_key_here
GOOGLE_CREDENTIALS_PATH=credentials.json
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVAL_RESULTS=5
```

### 4. Start Backend Server
```bash
cd backend
python main.py
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Frontend
```bash
npm start
```

## Usage

### 1. First-Time Google Authentication
- When you first add a document, you'll be redirected to Google's OAuth flow
- Grant permissions to read your Google Docs
- The authentication token will be saved for future use

### 2. Adding Documents
1. Open your Google Doc
2. Make sure it's shared (at least view access for your account)
3. Copy the document ID from the URL: `docs.google.com/document/d/[DOCUMENT_ID]/edit`
4. Paste the ID in the Document Manager
5. Click "Add Document"

### 3. Using the Chatbot
- Enable "Use RAG" checkbox to use document context
- Ask questions related to your uploaded documents
- The chatbot will show which documents it's referencing

## Features

### Document Processing
- Automatic text extraction from Google Docs
- Intelligent chunking with overlap
- Metadata preservation (title, source, etc.)

### Vector Storage
- ChromaDB for efficient similarity search
- Sentence-BERT embeddings for semantic understanding
- Persistent storage across sessions

### RAG Pipeline
- Context retrieval based on query similarity
- Prompt enhancement with relevant document sections
- Source attribution in responses

### API Endpoints
- `POST /documents/add` - Add Google Doc to knowledge base
- `DELETE /documents/{id}` - Remove document
- `GET /documents/stats` - View system statistics
- `DELETE /documents/clear` - Clear all documents
- `POST /chat/stream` - Chat with RAG enhancement

## Troubleshooting

### Google Authentication Issues
- Ensure credentials.json is in the correct location
- Check that Google Docs API is enabled
- Verify document sharing permissions

### Vector Store Issues
- Check ChromaDB path permissions
- Ensure sufficient disk space
- Restart backend if embeddings fail

### Performance Optimization
- Adjust chunk size for your document types
- Modify similarity threshold in RAG service
- Increase max_retrieval_results for more context

## Security Notes
- Keep credentials.json secure and never commit to version control
- Use environment variables for all sensitive configuration
- Consider implementing user authentication for production use

## Next Steps
- Add support for other document formats (PDF, Word)
- Implement user-specific document collections
- Add document versioning and update detection
- Enhance with more sophisticated NLP preprocessing