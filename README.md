# RAG-Enhanced PDF Chatbot

A comprehensive RAG (Retrieval-Augmented Generation) chatbot that processes PDF documents to provide context-aware responses. Upload PDFs directly or sync entire folders from Google Drive.

## 🚀 Features

### Document Management
- **📁 Direct PDF Upload**: Drag and drop or select PDF files directly from your computer
- **🔗 Google Drive Integration**: Sync entire folders or individual PDFs from Google Drive
- **🔄 Smart Sync**: Only process new or updated documents to save time
- **⏰ Auto-sync**: Configurable automatic synchronization at set intervals

### RAG Pipeline
- **🧠 Context-aware Responses**: Get answers based on your uploaded PDF content
- **🔍 Semantic Search**: Advanced vector similarity search using embeddings
- **📚 Source Attribution**: See which documents the chatbot references in responses
- **⚡ Streaming Chat**: Real-time streaming responses for better user experience

### PDF Processing
- **📄 Multi-method Text Extraction**: Uses both pdfplumber and PyPDF2 for best results
- **✂️ Intelligent Chunking**: Breaks documents into optimal chunks with overlap
- **🏷️ Metadata Preservation**: Maintains document titles, URLs, and modification dates

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── services/           # Core services (Google Drive, RAG, Vector Store, PDF Processing)
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration management
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/              # React components and logic
│   └── package.json      # Node.js dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Together AI API key
- Google Cloud Console account (optional, for Google Drive integration)

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
   - Optionally set up Google Drive API credentials for folder sync

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

## 📖 Usage

### Adding PDF Documents

**Option 1: Direct Upload (Recommended for individual files)**
1. Go to the "Individual PDFs" tab
2. Click "Upload PDF" sub-tab
3. Drag and drop a PDF file or click to select
4. Optionally add a custom title
5. Click "Upload PDF"

**Option 2: Google Drive Folder Sync (Recommended for multiple files)**
1. Upload your PDF documents to a Google Drive folder
2. Get the folder ID from the URL: `drive.google.com/drive/folders/[FOLDER_ID]`
3. Use the "Folder Sync" tab in the application
4. Enter the folder ID (or leave empty for entire Drive)
5. Click "Scan for PDFs" to preview, then "Sync" to add to knowledge base

**Option 3: Individual Google Drive Files**
1. Upload PDF to Google Drive and ensure it's shared
2. Get the file ID from URL: `drive.google.com/file/d/[FILE_ID]/view`
3. Use the "Individual PDFs" tab → "Google Drive" sub-tab
4. Enter the file ID and optional custom title
5. Click "Add PDF Document"

### Using the Chatbot

1. **Enable RAG**: Toggle "Use RAG (Document Context)" to enable context-aware responses
2. **Ask Questions**: Type questions related to your uploaded PDF documents
3. **View Sources**: The chatbot will show which documents it references
4. **Monitor Stats**: Check the knowledge base statistics to see indexed content

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
TOGETHER_API_KEY=your_together_api_key_here

# Google Drive Integration (Optional)
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

### Google Drive Setup (Optional)

1. **Get Google Drive API Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project and enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download and save as `backend/credentials.json`

2. **First-time Authentication**:
   - When you first use Google Drive features, you'll be redirected to Google's OAuth flow
   - Grant permissions to read your Google Drive files
   - The authentication token will be saved for future use

## 🔌 API Endpoints

### Document Management
- `POST /documents/upload` - Upload PDF file directly
- `POST /documents/add` - Add individual PDF document from Google Drive
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

## 🏗️ Architecture

### Backend Services
- **FileUploadService**: Handles direct PDF file uploads and validation
- **GoogleDriveService**: Handles Google Drive API integration and file downloads
- **PDFProcessor**: Extracts text from PDF files using multiple methods
- **DocumentProcessor**: Chunks documents and prepares them for vector storage
- **VectorStore**: Manages ChromaDB for semantic similarity search
- **RAGService**: Orchestrates retrieval and generation pipeline
- **DriveSyncService**: Manages folder synchronization and state tracking

### Frontend Components
- **FileUploadManager**: Interface for direct PDF file uploads with drag-and-drop
- **DriveManager**: Interface for folder-based PDF synchronization
- **DocumentManager**: Interface for individual PDF document management
- **ChatBox**: Streaming chat interface with RAG toggle
- **Statistics Dashboard**: Real-time system statistics and document info

## 📋 Supported File Types
- **PDF Documents**: Primary supported format with advanced text extraction
- **File Size Limit**: 50MB maximum per upload
- **Text Extraction**: Works best with text-based PDFs (scanned images may have limited extraction)

## 🔧 Troubleshooting

### Common Issues

**PDF Upload Issues**:
- Ensure PDF files are not password-protected
- Check file size is under 50MB limit
- Some scanned PDFs may have limited text extraction

**Google Drive Authentication**:
- Ensure `credentials.json` is properly configured
- Delete `token.pickle` and restart if authentication fails
- Check that Google Drive API is enabled in your project

**Vector Store Issues**:
- Ensure sufficient disk space for ChromaDB
- Check write permissions for the database directory
- Restart backend if embedding generation fails

**Performance Optimization**:
- Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your document types
- Increase `MAX_RETRIEVAL_RESULTS` for more comprehensive context
- Use folder sync instead of individual documents for better efficiency

## 🛡️ Security Notes
- Keep `credentials.json` secure and never commit to version control
- Use environment variables for all sensitive configuration
- Consider implementing user authentication for production deployment
- Regularly rotate API keys and review access permissions

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License
MIT License - see LICENSE file for details

## 🆘 Support
For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Create an issue on GitHub with detailed information about your problem

---

**Get started by uploading your first PDF document and asking questions about its content!**