# ⚖️ Legal AI Assistant - RAG-Enhanced PDF Chatbot

A comprehensive RAG (Retrieval-Augmented Generation) legal assistant that processes legal PDF documents to provide expert legal analysis and guidance. Upload legal documents and get intelligent, context-aware legal advice based on your document content with specialized legal AI analysis. **Features automatic cache clearing when the application is closed to maintain confidentiality.**

## 🚀 Features

### Legal Document Management
- **📁 Direct Legal PDF Upload**: Drag and drop or select legal PDF files (contracts, policies, briefs, etc.)
- **🔄 Advanced Legal Text Processing**: Specialized text extraction optimized for legal documents
- **📚 Legal Knowledge Base**: Persistent storage of processed legal documents with vector embeddings
- **🗑️ Confidential Auto-cleanup**: Automatically clears all legal documents when application closes

### Legal AI Analysis
- **⚖️ Legal-Specialized LLM**: Uses Llama-3.1-70B-Instruct-Turbo optimized for legal analysis
- **🧠 Always-On Legal Context**: RAG permanently enabled for accurate legal guidance
- **🔍 Legal Semantic Search**: Advanced vector similarity search for legal concepts
- **📚 Legal Source Attribution**: See which legal documents the AI references in responses
- **⚡ Streaming Legal Analysis**: Real-time streaming responses for complex legal questions

### Legal Document Processing
- **📄 Multi-method Legal Text Extraction**: Optimized for legal PDFs using pdfplumber and PyPDF2
- **✂️ Legal-Aware Chunking**: Breaks legal documents into contextually meaningful chunks
- **🏷️ Legal Metadata Preservation**: Maintains document titles, sources, and legal context

### Legal System Management
- **🧹 Confidential Cache Clearing**: Automatically cleans up all legal documents and data on close
- **💾 Secure Memory Management**: Efficient cleanup of legal vector databases and embeddings
- **🔄 Fresh Legal Sessions**: Each session starts clean for maximum confidentiality
- **🔒 Legal Confidentiality**: No persistent storage of legal documents between sessions

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend with legal AI
│   ├── services/           # Legal RAG, Vector Store, PDF Processing, File Upload
│   ├── main.py            # FastAPI application with legal prompt engineering
│   ├── config.py          # Legal AI model configuration
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend with legal UI
│   ├── src/              # React components with legal-specific design
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
   LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct-Turbo
   LLM_TEMPERATURE=0.1
   LLM_MAX_TOKENS=4000
   LLM_TOP_P=0.9
   ```

### Running the Legal AI Assistant

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

## 📖 Legal Usage

### Adding Legal Documents

1. **Direct Legal Upload**
   - Drag and drop legal PDF files into the upload area
   - Or click "Select Legal PDF" to browse and select
   - Supported: Contracts, policies, legal briefs, regulations, court documents
   - Optionally add a custom title for the document
   - Click "Upload Legal Document" to process and add to knowledge base

2. **Supported Legal Files**
   - PDF format only
   - Maximum file size: 50MB
   - Text-based legal PDFs work best
   - Contracts, agreements, policies, briefs, regulations, etc.

### Using the Legal AI Assistant

1. **Legal AI Always Enabled**: The assistant automatically uses your uploaded legal documents for expert legal analysis
2. **Ask Legal Questions**: 
   - "What are the key terms and conditions in this contract?"
   - "Explain the legal implications of this clause"
   - "What are my rights and obligations under this agreement?"
   - "Are there any potential legal risks in this document?"
3. **View Legal Sources**: The AI shows which legal documents it references in responses
4. **Monitor Legal Stats**: Check the legal knowledge base statistics

### Legal Cache Management

- **Automatic Confidential Cleanup**: Legal documents and cache are automatically cleared when you:
  - Close the browser tab/window
  - Navigate away from the application
  - Shut down the backend server
  - Exit the application
- **Fresh Legal Sessions**: Each time you start, you begin with a clean, confidential slate
- **Manual Legal Cleanup**: Use `npm run cleanup` to manually clear legal cache if needed

## 🔧 Legal Configuration

### Environment Variables (.env)
```env
# Required
TOGETHER_API_KEY=your_together_api_key_here

# Legal AI Model Configuration
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct-Turbo
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
LLM_TOP_P=0.9

# Vector Store Configuration
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Legal Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVAL_RESULTS=5
```

## 🔌 Legal API Endpoints

### Legal Document Management
- `POST /documents/upload` - Upload legal PDF file directly
- `DELETE /documents/{id}` - Remove legal document from knowledge base
- `GET /documents/stats` - View legal system statistics and document info
- `DELETE /documents/clear` - Clear all legal documents from knowledge base

### Legal Chat Interface
- `POST /chat/stream` - Chat with legal AI analysis and streaming responses (always enabled)

### Health Check
- `GET /health` - Check legal system health and AI model status

## 🏗️ Legal AI Architecture

### Backend Legal Services
- **FileUploadService**: Handles direct legal PDF file uploads and validation
- **PDFProcessor**: Extracts text from legal PDF files using multiple methods
- **DocumentProcessor**: Chunks legal documents and prepares them for vector storage
- **VectorStore**: Manages ChromaDB for legal semantic similarity search
- **RAGService**: Orchestrates legal retrieval and generation pipeline with legal prompts
- **Cleanup Handlers**: Automatic confidential cache clearing on application shutdown

### Frontend Legal Components
- **FileUploadManager**: Interface for direct legal PDF file uploads with legal-specific UI
- **DocumentManager**: Interface for legal PDF document management and statistics
- **ChatBox**: Streaming legal chat interface with legal AI always enabled
- **Cleanup Logic**: Automatic confidential cache clearing on component unmount and page close

### Legal Cache Management
- **Signal Handlers**: Graceful shutdown with confidential cleanup on SIGINT/SIGTERM
- **Event Listeners**: Browser event handling for tab/window close with legal data cleanup
- **Automatic Legal Cleanup**: Removes ChromaDB, temporary files, and legal authentication tokens
- **Legal Memory Management**: Efficient cleanup of legal vector embeddings and document storage

## 📋 Supported Legal File Types
- **Legal PDF Documents**: Contracts, agreements, policies, briefs, regulations, court documents
- **File Size Limit**: 50MB maximum per legal upload
- **Text Extraction**: Works best with text-based legal PDFs (scanned legal images may have limited extraction)

## ⚖️ Legal AI Model Details

### Llama-3.1-70B-Instruct-Turbo
- **Specialized for Legal Analysis**: Optimized for legal document interpretation
- **Legal Prompt Engineering**: Custom prompts designed for legal contexts
- **Legal Terminology**: Understands legal concepts, terminology, and precedents
- **Conservative Temperature**: Set to 0.1 for consistent, reliable legal analysis
- **Extended Context**: 4000 max tokens for comprehensive legal responses

### Legal Prompt Features
- **Legal Context Awareness**: Distinguishes between document content and general legal knowledge
- **Legal Citation**: References specific sections and provisions from documents
- **Legal Disclaimers**: Always includes appropriate legal disclaimers
- **Legal Guidance**: Provides actionable legal guidance while recommending attorney consultation

## 🔧 Legal Troubleshooting

### Common Legal Issues

**Legal PDF Upload Issues**:
- Ensure legal PDF files are not password-protected
- Check file size is under 50MB limit
- Some scanned legal documents may have limited text extraction

**Legal Cache Issues**:
- If legal cache isn't clearing automatically, use `npm run cleanup`
- Ensure proper permissions for legal file/directory deletion
- Check logs for legal cleanup errors

**Legal Vector Store Issues**:
- Ensure sufficient disk space for legal ChromaDB
- Check write permissions for the legal database directory
- Restart backend if legal embedding generation fails

**Legal Performance Optimization**:
- Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your legal document types
- Increase `MAX_RETRIEVAL_RESULTS` for more comprehensive legal context
- Monitor memory usage with large legal document collections

## 🛡️ Legal Security & Confidentiality

- **Confidential Processing**: All legal documents processed locally with automatic cleanup
- **No Persistent Storage**: Legal documents never stored permanently between sessions
- **Secure API Keys**: Use environment variables for all sensitive legal configuration
- **Legal Disclaimers**: Always includes appropriate legal disclaimers in responses
- **Attorney Consultation**: Consistently recommends consulting qualified attorneys
- **Data Privacy**: Legal document content never leaves your local environment

## ⚠️ Legal Disclaimers

### Important Legal Notice
This AI assistant provides general legal information and document analysis. It does not constitute legal advice and should not replace consultation with a qualified attorney for specific legal matters.

### What This Tool Does
- Analyzes legal document content and structure
- Explains legal concepts and terminology
- Identifies key provisions and clauses
- Provides general legal guidance and information

### What This Tool Does NOT Do
- Provide specific legal advice for your situation
- Replace the need for qualified legal counsel
- Guarantee legal accuracy or completeness
- Create attorney-client privilege

### Recommendations
- Always consult with a qualified attorney for specific legal advice
- Use this tool as a starting point for legal document analysis
- Verify all legal information with appropriate legal professionals
- Consider the limitations of AI in complex legal matters

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes with legal considerations
4. Add tests if applicable
5. Submit a pull request

## 📄 License
MIT License - see LICENSE file for details

## 🆘 Legal Support
For legal AI issues and questions:
1. Check the legal troubleshooting section above
2. Review the legal API documentation
3. Create an issue on GitHub with detailed information about your legal AI problem

---

**⚖️ Get started by uploading your first legal PDF document and asking legal questions about its content! Legal AI analysis is always enabled for expert legal guidance, and everything is automatically cleared when you're done to maintain confidentiality.**

**Remember: This tool provides legal information, not legal advice. Always consult with a qualified attorney for specific legal matters.**