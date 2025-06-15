# RAG-Enhanced PDF Chatbot

A comprehensive RAG (Retrieval-Augmented Generation) chatbot that integrates with Google Drive to provide context-aware responses based on your PDF document content.

## Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── services/           # Core services (Google Drive, RAG, Vector Store, PDF Processing)
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration management
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/              # React components and logic
│   └── package.json      # Node.js dependencies
└── setup_instructions.md # Detailed setup guide
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Google Cloud Console account
- Together AI API key

### Installation

1. **Install all dependencies:**
   ```bash
   npm run install-all
   ```

   Or install separately:
   ```bash
   # Backend dependencies
   cd backend
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd frontend
   npm install
   ```

2. **Configure environment:**
   - Copy `backend/.env.example` to `backend/.env`
   - Add your Together AI API key
   - Set up Google Drive API credentials (see setup_instructions.md)

### Running the Application

**Start both services simultaneously:**
```bash
npm run dev
```

Or start them separately:

1. **Start the backend server:**
   ```bash
   npm run backend
   # or: cd backend && python main.py
   ```

2. **Start the frontend (in a new terminal):**
   ```bash
   npm run frontend
   # or: cd frontend && npm start
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Features

### Document Management
- **PDF Folder Sync**: Automatically sync entire Google Drive folders containing PDF documents
- **Individual PDF Management**: Add specific PDF documents by ID or URL
- **Smart Sync**: Only process new or updated documents to save time
- **Auto-sync**: Configurable automatic synchronization at set intervals

### RAG Pipeline
- **Context-aware Responses**: Get answers based on your uploaded PDF content
- **Semantic Search**: Advanced vector similarity search using embeddings
- **Source Attribution**: See which documents the chatbot references in responses
- **Streaming Chat**: Real-time streaming responses for better user experience

### PDF Processing
- **Multi-method Text Extraction**: Uses both pdfplumber and PyPDF2 for best results
- **Intelligent Chunking**: Breaks documents into optimal chunks with overlap
- **Metadata Preservation**: Maintains document titles, URLs, and modification dates

## API Endpoints

### Document Management
- `POST /documents/add` - Add individual PDF document to knowledge base
- `DELETE /documents/{id}` - Remove document from knowledge base
- `GET /documents/stats` - View system statistics and document info
- `DELETE /documents/clear` - Clear all documents from knowledge base

### Google Drive Integration
- `POST /drive/sync` - Sync PDF documents from Google Drive folder
- `POST /drive/scan` - Preview PDF documents in folder without syncing
- `GET /drive/sync/status` - Get current synchronization status
- `POST /drive/auto-sync` - Trigger automatic sync if needed

### Chat Interface
- `POST /chat/stream` - Chat with RAG enhancement and streaming responses

## Usage

### Setting Up Google Drive Integration

1. **Get Google Drive API Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project and enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download and save as `backend/credentials.json`

2. **Configure Environment**:
   - Set your Together AI API key in `backend/.env`
   - Optionally set a default folder ID for automatic syncing

### Adding PDF Documents

**Option 1: Folder Sync (Recommended)**
1. Upload your PDF documents to a Google Drive folder
2. Get the folder ID from the URL: `drive.google.com/drive/folders/[FOLDER_ID]`
3. Use the "PDF Folder Sync" tab in the application
4. Enter the folder ID (or leave empty for entire Drive)
5. Click "Scan for PDFs" to preview, then "Sync" to add to knowledge base

**Option 2: Individual Documents**
1. Upload PDF to Google Drive and ensure it's shared
2. Get the file ID from URL: `drive.google.com/file/d/[FILE_ID]/view`
3. Use the "Individual PDFs" tab in the application
4. Enter the file ID and optional custom title
5. Click "Add PDF Document"

### Using the Chatbot

1. **Enable RAG**: Toggle "Use RAG (Document Context)" to enable context-aware responses
2. **Ask Questions**: Type questions related to your uploaded PDF documents
3. **View Sources**: The chatbot will show which documents it references
4. **Monitor Stats**: Check the knowledge base statistics to see indexed content

## Configuration

### Environment Variables (.env)
```env
# Required
TOGETHER_API_KEY=your_together_api_key_here

# Google Drive Integration
GOOGLE_CREDENTIALS_PATH=credentials.json

# Vector Store Configuration
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVAL_RESULTS=5

# Auto-sync Settings
DRIVE_SYNC_INTERVAL_HOURS=24
DEFAULT_DRIVE_FOLDER_ID=your_default_folder_id_here
```

### Supported File Types
- **PDF Documents**: Primary supported format with advanced text extraction
- **Future Support**: Additional formats can be added by extending the document processor

## Architecture

### Backend Services
- **GoogleDriveService**: Handles Google Drive API integration and file downloads
- **PDFProcessor**: Extracts text from PDF files using multiple methods
- **DocumentProcessor**: Chunks documents and prepares them for vector storage
- **VectorStore**: Manages ChromaDB for semantic similarity search
- **RAGService**: Orchestrates retrieval and generation pipeline
- **DriveSyncService**: Manages folder synchronization and state tracking

### Frontend Components
- **DriveManager**: Interface for folder-based PDF synchronization
- **DocumentManager**: Interface for individual PDF document management
- **ChatBox**: Streaming chat interface with RAG toggle
- **Statistics Dashboard**: Real-time system statistics and document info

## Troubleshooting

### Common Issues

**Google Drive Authentication**:
- Ensure `credentials.json` is properly configured
- Delete `token.pickle` and restart if authentication fails
- Check that Google Drive API is enabled in your project

**PDF Processing Errors**:
- Verify PDF files are not password-protected
- Check file permissions in Google Drive
- Some scanned PDFs may have limited text extraction

**Vector Store Issues**:
- Ensure sufficient disk space for ChromaDB
- Check write permissions for the database directory
- Restart backend if embedding generation fails

**Performance Optimization**:
- Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your document types
- Increase `MAX_RETRIEVAL_RESULTS` for more comprehensive context
- Use folder sync instead of individual documents for better efficiency

## Development

### Adding New Document Types
1. Extend `PDFProcessor` or create new processor class
2. Update `GoogleDriveService` to handle new MIME types
3. Modify frontend to support new file type selection

### Customizing RAG Pipeline
- Modify `RAGService.generate_rag_prompt()` for different prompt templates
- Adjust similarity thresholds in `VectorStore.search()`
- Implement custom embedding models in `VectorStore`

## Security Notes
- Keep `credentials.json` secure and never commit to version control
- Use environment variables for all sensitive configuration
- Consider implementing user authentication for production deployment
- Regularly rotate API keys and review access permissions

## License
MIT License - see LICENSE file for details

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

For detailed setup instructions and advanced configuration, see `setup_instructions.md`.