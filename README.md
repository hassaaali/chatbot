# ⚖️ Legal AI Assistant - RAG-Enhanced PDF Chatbot (Together AI)

A comprehensive RAG (Retrieval-Augmented Generation) legal assistant powered by **Together AI** that processes legal PDF documents to provide expert legal analysis and guidance. Upload legal documents and get intelligent, context-aware legal advice using state-of-the-art AI models from Together AI. **Features automatic cache clearing when the application is closed to maintain confidentiality.**

## 🚀 Features

### Legal Document Management
- **📁 Direct Legal PDF Upload**: Drag and drop or select legal PDF files (contracts, policies, briefs, etc.)
- **🔄 Advanced Legal Text Processing**: Specialized text extraction optimized for legal documents
- **📚 Legal Knowledge Base**: Persistent storage of processed legal documents with vector embeddings
- **🗑️ Confidential Auto-cleanup**: Automatically clears all legal documents when application closes

### Together AI Integration
- **🤖 Multiple AI Models**: Choose from various Together AI models optimized for legal analysis
- **⚖️ Legal-Specialized Processing**: Custom prompts and processing designed for legal contexts
- **🧠 Always-On Legal Context**: RAG permanently enabled for accurate legal guidance
- **🔍 Legal Semantic Search**: Advanced vector similarity search for legal concepts
- **📚 Legal Source Attribution**: See which legal documents the AI references in responses
- **⚡ Streaming Legal Analysis**: Real-time streaming responses for complex legal questions

### Available AI Models
- **meta-llama/Llama-2-7b-chat-hf**: Llama 2 7B - Fast and efficient for legal Q&A
- **meta-llama/Llama-2-13b-chat-hf**: Llama 2 13B - Balanced performance for legal analysis
- **meta-llama/Llama-2-70b-chat-hf**: Llama 2 70B - Most capable for complex legal reasoning
- **mistralai/Mistral-7B-Instruct-v0.1**: Mistral 7B - Excellent instruction following for legal tasks
- **mistralai/Mixtral-8x7B-Instruct-v0.1**: Mixtral 8x7B - Advanced reasoning for legal documents
- **codellama/CodeLlama-7b-Instruct-hf**: Code Llama 7B - Good for legal logic and structured analysis

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
├── backend/                 # Python FastAPI backend with Together AI integration
│   ├── services/           # Legal RAG, Vector Store, PDF Processing, Together AI Client
│   ├── main.py            # FastAPI application with Together AI streaming
│   ├── config.py          # Together AI API configuration
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend with model selection
│   ├── src/              # React components with Together AI integration
│   └── package.json      # Node.js dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- **Together AI API key** (get one at [together.ai](https://together.ai))

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
   LLM_MODEL=meta-llama/Llama-2-7b-chat-hf
   LLM_TEMPERATURE=0.1
   LLM_MAX_TOKENS=2000
   LLM_TOP_P=0.9
   ```

### Getting Your Together AI API Key

1. Go to [together.ai](https://together.ai) and create an account
2. Navigate to your [API Keys](https://api.together.xyz/settings/api-keys) section
3. Create a new API key
4. Copy the key and add it to your `.env` file

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
   - Available Models: http://localhost:8000/models

### Manual Cache Cleanup

If you need to manually clean the cache:
```bash
npm run cleanup
```

## 📖 Legal Usage

### Selecting AI Models

1. **Model Selection**: Use the dropdown in the chat interface to select different Together AI models
2. **Recommended Models**:
   - **Llama-2-7b-chat-hf**: Fast and efficient for general legal Q&A
   - **Llama-2-13b-chat-hf**: Balanced performance for detailed legal analysis
   - **Llama-2-70b-chat-hf**: Most capable for complex legal reasoning
   - **Mistral-7B-Instruct-v0.1**: Excellent for instruction-following legal tasks
   - **Mixtral-8x7B-Instruct-v0.1**: Advanced reasoning for complex legal documents

### Adding Legal Documents

1. **Direct Legal Upload**
   - Drag and drop legal PDF files into the upload area
   - Or click "Select Legal PDF" to browse and select
   - Supported: Contracts, policies, legal briefs, regulations, court documents
   - Optionally add a custom title for the document
   - Click "Upload Legal Document" to process and add to knowledge base

2. **Supported Legal Files**
   - PDF format only
   - Maximum file size: 10MB
   - Text-based legal PDFs work best
   - Contracts, agreements, policies, briefs, regulations, etc.

### Using the Legal AI Assistant

1. **Together AI Always Enabled**: The assistant automatically uses your uploaded legal documents for expert legal analysis
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

## 🔧 Together AI Configuration

### Environment Variables (.env)
```env
# Required - Together AI API
TOGETHER_API_KEY=your_together_api_key_here
TOGETHER_API_URL=https://api.together.xyz/v1/chat/completions

# Legal AI Model Configuration
LLM_MODEL=meta-llama/Llama-2-7b-chat-hf
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
LLM_TOP_P=0.9

# Vector Store Configuration
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Legal Document Processing
CHUNK_SIZE=500
CHUNK_OVERLAP=100
MAX_RETRIEVAL_RESULTS=3

# Together AI API Settings
TOGETHER_REQUEST_TIMEOUT=120
TOGETHER_MAX_RETRIES=3
```

## 🔌 Legal API Endpoints

### Legal Document Management
- `POST /documents/upload` - Upload legal PDF file directly
- `DELETE /documents/{id}` - Remove legal document from knowledge base
- `GET /documents/stats` - View legal system statistics and document info
- `DELETE /documents/clear` - Clear all legal documents from knowledge base

### Together AI Integration
- `GET /models` - Get available Together AI models for legal analysis
- `POST /chat/stream` - Chat with Together AI analysis and streaming responses

### Health Check
- `GET /health` - Check legal system health and Together AI API status

## 🏗️ Legal AI Architecture

### Backend Legal Services
- **TogetherClient**: Direct integration with Together AI API
- **FileUploadService**: Handles direct legal PDF file uploads and validation
- **PDFProcessor**: Extracts text from legal PDF files using multiple methods
- **DocumentProcessor**: Chunks legal documents and prepares them for vector storage
- **VectorStore**: Manages ChromaDB for legal semantic similarity search
- **RAGService**: Orchestrates legal retrieval and generation pipeline with legal prompts

### Frontend Legal Components
- **Model Selector**: Interface for choosing Together AI models
- **FileUploadManager**: Interface for direct legal PDF file uploads with legal-specific UI
- **DocumentManager**: Interface for legal PDF document management and statistics
- **ChatBox**: Streaming legal chat interface with Together AI integration

### Together AI Integration
- **Multiple Model Support**: Easy switching between Llama 2, Mistral, CodeLlama, and other models
- **Streaming Responses**: Real-time streaming from Together AI API
- **Error Handling**: Robust error handling with automatic retries
- **Rate Limit Handling**: Automatic handling of API rate limits

## 📋 Supported Legal File Types
- **Legal PDF Documents**: Contracts, agreements, policies, briefs, regulations, court documents
- **File Size Limit**: 10MB maximum per legal upload
- **Text Extraction**: Works best with text-based legal PDFs

## 🤖 Together AI Model Details

### Available Models

#### meta-llama/Llama-2-7b-chat-hf
- **Best for**: Fast legal Q&A and general legal assistance
- **Strengths**: Quick responses, good general legal knowledge
- **Use case**: Initial legal consultations and quick document reviews

#### meta-llama/Llama-2-13b-chat-hf
- **Best for**: Balanced legal analysis with good performance
- **Strengths**: Better reasoning than 7B, still fast
- **Use case**: Detailed contract analysis and legal explanations

#### meta-llama/Llama-2-70b-chat-hf
- **Best for**: Complex legal reasoning and comprehensive analysis
- **Strengths**: Most capable model, excellent for complex legal matters
- **Use case**: Complex legal document analysis and sophisticated legal reasoning

#### mistralai/Mistral-7B-Instruct-v0.1
- **Best for**: Instruction-following and structured legal analysis
- **Strengths**: Excellent at following specific legal instructions
- **Use case**: Specific legal tasks and structured document analysis

#### mistralai/Mixtral-8x7B-Instruct-v0.1
- **Best for**: Advanced legal reasoning and complex document analysis
- **Strengths**: Mixture of experts architecture for sophisticated reasoning
- **Use case**: Complex legal research and multi-document analysis

#### codellama/CodeLlama-7b-Instruct-hf
- **Best for**: Legal logic and structured legal analysis
- **Strengths**: Good at logical reasoning and structured thinking
- **Use case**: Contract logic analysis and legal procedure understanding

### Legal Prompt Features
- **Legal Context Awareness**: Distinguishes between document content and general legal knowledge
- **Legal Citation**: References specific sections and provisions from documents
- **Legal Disclaimers**: Always includes appropriate legal disclaimers
- **Legal Guidance**: Provides actionable legal guidance while recommending attorney consultation

## 🔧 Legal Troubleshooting

### Common Together AI Issues

**API Key Issues**:
- Ensure your Together AI API key is valid and active
- Check that the key is correctly set in your `.env` file
- Verify your Together AI account has sufficient credits

**Rate Limiting**:
- Together AI has rate limits that are automatically handled
- The system will retry with exponential backoff
- Consider upgrading your Together AI plan for higher limits

**Legal PDF Upload Issues**:
- Ensure legal PDF files are not password-protected
- Check file size is under 10MB limit
- Some scanned legal documents may have limited text extraction

**Legal Performance Optimization**:
- Choose appropriate models based on your use case (7B for speed, 70B for quality)
- Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your legal document types
- Monitor API usage and costs in your Together AI dashboard

## 🛡️ Legal Security & Confidentiality

- **Confidential Processing**: All legal documents processed locally with automatic cleanup
- **No Persistent Storage**: Legal documents never stored permanently between sessions
- **Secure API Keys**: Use environment variables for all sensitive configuration
- **Together AI Privacy**: Requests to Together AI API follow their privacy policy
- **Legal Disclaimers**: Always includes appropriate legal disclaimers in responses
- **Attorney Consultation**: Consistently recommends consulting qualified attorneys

## ⚠️ Legal Disclaimers

### Important Legal Notice
This AI assistant provides general legal information and document analysis using Together AI models. It does not constitute legal advice and should not replace consultation with a qualified attorney for specific legal matters.

### What This Tool Does
- Analyzes legal document content and structure using advanced AI
- Explains legal concepts and terminology with AI assistance
- Identifies key provisions and clauses using machine learning
- Provides general legal guidance and information through AI analysis

### What This Tool Does NOT Do
- Provide specific legal advice for your situation
- Replace the need for qualified legal counsel
- Create attorney-client privilege
- Guarantee legal accuracy or completeness

### Recommendations
- Always consult with a qualified attorney for specific legal advice
- Use this tool as a starting point for legal document analysis
- Verify all AI-generated legal information with appropriate legal professionals
- Consider the limitations of AI in complex legal matters

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes with Together AI considerations
4. Add tests if applicable
5. Submit a pull request

## 📄 License
MIT License - see LICENSE file for details

## 🆘 Legal Support
For Together AI legal AI issues and questions:
1. Check the Together AI troubleshooting section above
2. Review the Together AI API documentation
3. Create an issue on GitHub with detailed information about your problem

---

**⚖️ Get started by uploading your first legal PDF document and asking legal questions! Together AI analysis is always enabled for expert legal guidance, and everything is automatically cleared when you're done to maintain confidentiality.**

**🤖 Powered by Together AI**: Access to state-of-the-art language models including Llama 2, Mistral, and CodeLlama for superior legal analysis.

**Remember: This tool provides legal information, not legal advice. Always consult with a qualified attorney for specific legal matters.**