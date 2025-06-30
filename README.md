# RAG-Enhanced PDF Chatbot

A comprehensive RAG (Retrieval-Augmented Generation) chatbot that processes PDF documents to provide context-aware responses. Upload PDFs directly and get intelligent answers based on your document content with RAG always enabled for the best experience. **Features automatic cache clearing when the application is closed to keep your system clean.**

## 🚀 Features

### Document Management
- **📁 Direct PDF Upload**: Drag and drop or select PDF files directly from your computer
- **🔄 Smart Processing**: Advanced text extraction using multiple PDF processing methods
- **📚 Knowledge Base**: Persistent storage of processed documents with vector embeddings
- **🗑️ Auto-cleanup**: Automatically clears cache and temporary files when application closes

### RAG Pipeline
- **🧠 Always-On Context**: RAG is permanently enabled for the most accurate responses
- **🔍 Semantic Search**: Advanced vector similarity search using embeddings
- **📚 Source Attribution**: See which documents the chatbot references in responses
- **⚡ Streaming Chat**: Real-time streaming responses for better user experience

### PDF Processing
- **📄 Multi-method Text Extraction**: Uses both pdfplumber and PyPDF2 for best results
- **✂️ Intelligent Chunking**: Breaks documents into optimal chunks with overlap
- **🏷️ Metadata Preservation**: Maintains document titles and processing information

### System Management
- **🧹 Automatic Cache Clearing**: Cleans up all documents and temporary files on application close
- **💾 Memory Management**: Efficient cleanup of vector databases and embeddings
- **🔄 Fresh Start**: Each session starts with a clean slate for optimal performance

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── services/           # Core services (RAG, Vector Store, PDF Processing, File Upload)
│   ├── main.py            # FastAPI application with cleanup handlers
│   ├── config.py          # Configuration management
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/              # React components with cleanup logic
│   └── package.json      # Node.js dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
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
   - Add your Together AI API key:
   ```env
   TOGETHER_API_KEY=your_together_api_key_here
   ```

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

### Manual Cache Cleanup

If you need to manually clean the cache:
```bash
npm run cleanup
```

## 📖 Usage

### Adding PDF Documents

1. **Direct Upload**
   - Drag and drop a PDF file into the upload area
   - Or click "Select PDF File" to browse and select
   - Optionally add a custom title for the document
   - Click "Upload PDF" to process and add to knowledge base

2. **Supported Files**
   - PDF format only
   - Maximum file size: 50MB
   - Text-based PDFs work best (scanned images may have limited text extraction)

### Using the Chatbot

1. **RAG is Always Enabled**: The chatbot automatically uses your uploaded PDF documents for context-aware responses
2. **Ask Questions**: Type questions related to your uploaded PDF documents
3. **View Sources**: The chatbot will show which documents it references in responses
4. **Monitor Stats**: Check the knowledge base statistics to see indexed content

### Cache Management

- **Automatic Cleanup**: Documents and cache are automatically cleared when you:
  - Close the browser tab/window
  - Navigate away from the application
  - Shut down the backend server
  - Exit the application
- **Fresh Sessions**: Each time you start the application, you begin with a clean slate
- **Manual Cleanup**: Use `npm run cleanup` to manually clear cache if needed

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
TOGETHER_API_KEY=your_together_api_key_here

# Vector Store Configuration
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVAL_RESULTS=5
```

## 🔌 API Endpoints

### Document Management
- `POST /documents/upload` - Upload PDF file directly
- `DELETE /documents/{id}` - Remove document from knowledge base
- `GET /documents/stats` - View system statistics and document info
- `DELETE /documents/clear` - Clear all documents from knowledge base

### Chat Interface
- `POST /chat/stream` - Chat with RAG enhancement and streaming responses (always enabled)

### Health Check
- `GET /health` - Check system health and service status

## 🏗️ Architecture

### Backend Services
- **FileUploadService**: Handles direct PDF file uploads and validation
- **PDFProcessor**: Extracts text from PDF files using multiple methods
- **DocumentProcessor**: Chunks documents and prepares them for vector storage
- **VectorStore**: Manages ChromaDB for semantic similarity search
- **RAGService**: Orchestrates retrieval and generation pipeline
- **Cleanup Handlers**: Automatic cache clearing on application shutdown

### Frontend Components
- **FileUploadManager**: Interface for direct PDF file uploads with drag-and-drop
- **DocumentManager**: Interface for PDF document management and statistics
- **ChatBox**: Streaming chat interface with RAG always enabled
- **Cleanup Logic**: Automatic cache clearing on component unmount and page close

### Cache Management
- **Signal Handlers**: Graceful shutdown with cleanup on SIGINT/SIGTERM
- **Event Listeners**: Browser event handling for tab/window close
- **Automatic Cleanup**: Removes ChromaDB, temporary files, and authentication tokens
- **Memory Management**: Efficient cleanup of vector embeddings and document storage

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

**Cache Issues**:
- If cache isn't clearing automatically, use `npm run cleanup`
- Ensure proper permissions for file/directory deletion
- Check logs for cleanup errors

**Vector Store Issues**:
- Ensure sufficient disk space for ChromaDB
- Check write permissions for the database directory
- Restart backend if embedding generation fails

**Performance Optimization**:
- Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your document types
- Increase `MAX_RETRIEVAL_RESULTS` for more comprehensive context
- Monitor memory usage with large document collections

## 🛡️ Security Notes
- Use environment variables for all sensitive configuration
- Consider implementing user authentication for production deployment
- Regularly rotate API keys and review access permissions
- Uploaded files are processed locally and automatically cleaned up
- No persistent storage of user documents between sessions

## 🧹 Cleanup Details

### What Gets Cleaned Up
- **ChromaDB Directory**: Complete vector database removal
- **Temporary Files**: All temp directories and uploaded files
- **Authentication Tokens**: OAuth tokens and session data
- **Document Cache**: All processed document chunks and embeddings
- **System Logs**: Cleanup operation logs

### When Cleanup Occurs
- **Browser Close**: When user closes tab or browser window
- **Page Navigation**: When user navigates away from the application
- **Server Shutdown**: When backend server is stopped (Ctrl+C)
- **Component Unmount**: When React components are unmounted
- **Manual Trigger**: When `npm run cleanup` is executed

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

**Get started by uploading your first PDF document and asking questions about its content! RAG is always enabled for the best experience, and everything is automatically cleaned up when you're done.**