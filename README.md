# ⚖️ Legal AI Assistant - RAG-Enhanced PDF Chatbot (Hugging Face)

A comprehensive RAG (Retrieval-Augmented Generation) legal assistant powered by **Hugging Face** that processes legal PDF documents to provide expert legal analysis and guidance. Upload legal documents and get intelligent, context-aware legal advice using state-of-the-art AI models from Hugging Face. **Features automatic cache clearing when the application is closed to maintain confidentiality.**

## 🚀 Features

### Legal Document Management
- **📁 Direct Legal PDF Upload**: Drag and drop or select legal PDF files (contracts, policies, briefs, etc.)
- **🔄 Advanced Legal Text Processing**: Specialized text extraction optimized for legal documents
- **📚 Legal Knowledge Base**: Persistent storage of processed legal documents with vector embeddings
- **🗑️ Confidential Auto-cleanup**: Automatically clears all legal documents when application closes

### Hugging Face AI Integration
- **🤖 Multiple AI Models**: Choose from various Hugging Face models optimized for legal analysis
- **⚖️ Legal-Specialized Processing**: Custom prompts and processing designed for legal contexts
- **🧠 Always-On Legal Context**: RAG permanently enabled for accurate legal guidance
- **🔍 Legal Semantic Search**: Advanced vector similarity search for legal concepts
- **📚 Legal Source Attribution**: See which legal documents the AI references in responses
- **⚡ Streaming Legal Analysis**: Real-time streaming responses for complex legal questions

### Available AI Models
- **microsoft/DialoGPT-large**: Large conversational model, excellent for legal Q&A
- **google/flan-t5-large**: Instruction-following model, superior for legal analysis
- **facebook/blenderbot-400M-distill**: Balanced model for legal document discussion
- **microsoft/GODEL-v1_1-large-seq2seq**: Goal-oriented model for legal guidance

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
├── backend/                 # Python FastAPI backend with Hugging Face integration
│   ├── services/           # Legal RAG, Vector Store, PDF Processing, HF Client
│   ├── main.py            # FastAPI application with Hugging Face streaming
│   ├── config.py          # Hugging Face API configuration
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend with model selection
│   ├── src/              # React components with Hugging Face integration
│   └── package.json      # Node.js dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- **Hugging Face API key** (free at [huggingface.co](https://huggingface.co))

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
   - Add your Hugging Face API key:
   ```env
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   LLM_MODEL=microsoft/DialoGPT-large
   LLM_TEMPERATURE=0.1
   LLM_MAX_TOKENS=2000
   LLM_TOP_P=0.9
   ```

### Getting Your Hugging Face API Key

1. Go to [huggingface.co](https://huggingface.co) and create a free account
2. Navigate to your [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Create a new token with "Read" permissions
4. Copy the token and add it to your `.env` file

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

1. **Model Selection**: Use the dropdown in the chat interface to select different Hugging Face models
2. **Recommended Models**:
   - **DialoGPT-large**: Best for conversational legal analysis
   - **flan-t5-large**: Excellent for instruction-following and legal reasoning
   - **GODEL**: Goal-oriented responses for specific legal guidance

### Adding Legal Documents

1. **Direct Legal Upload**
   - Drag and drop legal PDF files into the upload area
   - Or click "Select Legal PDF" to browse and select
   - Supported: Contracts, policies, legal briefs, regulations, court documents
   - Optionally add a custom title for the document
   - Click "Upload Legal Document" to process and add to knowledge base

2. **Supported Legal Files**
   - PDF format only
   - Maximum file size: 10MB (optimized for performance)
   - Text-based legal PDFs work best
   - Contracts, agreements, policies, briefs, regulations, etc.

### Using the Legal AI Assistant

1. **Hugging Face AI Always Enabled**: The assistant automatically uses your uploaded legal documents for expert legal analysis
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

## 🔧 Hugging Face Configuration

### Environment Variables (.env)
```env
# Required - Hugging Face API
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
HUGGINGFACE_API_URL=https://api-inference.huggingface.co/models

# Legal AI Model Configuration
LLM_MODEL=microsoft/DialoGPT-large
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

# Hugging Face API Settings
HF_REQUEST_TIMEOUT=120
HF_MAX_RETRIES=3
```

## 🔌 Legal API Endpoints

### Legal Document Management
- `POST /documents/upload` - Upload legal PDF file directly
- `DELETE /documents/{id}` - Remove legal document from knowledge base
- `GET /documents/stats` - View legal system statistics and document info
- `DELETE /documents/clear` - Clear all legal documents from knowledge base

### Hugging Face Integration
- `GET /models` - Get available Hugging Face models for legal analysis
- `POST /chat/stream` - Chat with Hugging Face AI analysis and streaming responses

### Health Check
- `GET /health` - Check legal system health and Hugging Face API status

## 🏗️ Legal AI Architecture

### Backend Legal Services
- **HuggingFaceClient**: Direct integration with Hugging Face Inference API
- **FileUploadService**: Handles direct legal PDF file uploads and validation
- **PDFProcessor**: Extracts text from legal PDF files using multiple methods
- **DocumentProcessor**: Chunks legal documents and prepares them for vector storage
- **VectorStore**: Manages ChromaDB for legal semantic similarity search
- **RAGService**: Orchestrates legal retrieval and generation pipeline with legal prompts

### Frontend Legal Components
- **Model Selector**: Interface for choosing Hugging Face models
- **FileUploadManager**: Interface for direct legal PDF file uploads with legal-specific UI
- **DocumentManager**: Interface for legal PDF document management and statistics
- **ChatBox**: Streaming legal chat interface with Hugging Face AI integration

### Hugging Face Integration
- **Multiple Model Support**: Easy switching between different AI models
- **Streaming Responses**: Real-time streaming from Hugging Face Inference API
- **Error Handling**: Robust error handling with automatic retries
- **Model Loading**: Automatic handling of model loading states

## 📋 Supported Legal File Types
- **Legal PDF Documents**: Contracts, agreements, policies, briefs, regulations, court documents
- **File Size Limit**: 10MB maximum per legal upload (optimized for Hugging Face processing)
- **Text Extraction**: Works best with text-based legal PDFs

## 🤖 Hugging Face Model Details

### Available Models

#### microsoft/DialoGPT-large
- **Best for**: Conversational legal analysis and Q&A
- **Strengths**: Natural dialogue, context understanding
- **Use case**: General legal questions and document discussion

#### google/flan-t5-large
- **Best for**: Instruction-following and structured legal analysis
- **Strengths**: Following complex instructions, reasoning
- **Use case**: Detailed legal analysis and specific tasks

#### facebook/blenderbot-400M-distill
- **Best for**: Balanced legal document discussion
- **Strengths**: Efficient processing, good general performance
- **Use case**: Quick legal consultations and document overview

#### microsoft/GODEL-v1_1-large-seq2seq
- **Best for**: Goal-oriented legal guidance
- **Strengths**: Task-focused responses, legal reasoning
- **Use case**: Specific legal advice and actionable guidance

### Legal Prompt Features
- **Legal Context Awareness**: Distinguishes between document content and general legal knowledge
- **Legal Citation**: References specific sections and provisions from documents
- **Legal Disclaimers**: Always includes appropriate legal disclaimers
- **Legal Guidance**: Provides actionable legal guidance while recommending attorney consultation

## 🔧 Legal Troubleshooting

### Common Hugging Face Issues

**API Key Issues**:
- Ensure your Hugging Face API key is valid and has proper permissions
- Check that the key is correctly set in your `.env` file
- Verify your Hugging Face account has API access

**Model Loading Issues**:
- Some models may take time to load on first use
- The system automatically retries with exponential backoff
- Try switching to a different model if one is consistently slow

**Legal PDF Upload Issues**:
- Ensure legal PDF files are not password-protected
- Check file size is under 10MB limit
- Some scanned legal documents may have limited text extraction

**Legal Performance Optimization**:
- Choose appropriate models based on your use case
- Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your legal document types
- Monitor memory usage with large legal document collections

## 🛡️ Legal Security & Confidentiality

- **Confidential Processing**: All legal documents processed locally with automatic cleanup
- **No Persistent Storage**: Legal documents never stored permanently between sessions
- **Secure API Keys**: Use environment variables for all sensitive configuration
- **Hugging Face Privacy**: Requests to Hugging Face API follow their privacy policy
- **Legal Disclaimers**: Always includes appropriate legal disclaimers in responses
- **Attorney Consultation**: Consistently recommends consulting qualified attorneys

## ⚠️ Legal Disclaimers

### Important Legal Notice
This AI assistant provides general legal information and document analysis using Hugging Face AI models. It does not constitute legal advice and should not replace consultation with a qualified attorney for specific legal matters.

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
3. Make your changes with Hugging Face considerations
4. Add tests if applicable
5. Submit a pull request

## 📄 License
MIT License - see LICENSE file for details

## 🆘 Legal Support
For Hugging Face legal AI issues and questions:
1. Check the Hugging Face troubleshooting section above
2. Review the Hugging Face API documentation
3. Create an issue on GitHub with detailed information about your problem

---

**⚖️ Get started by uploading your first legal PDF document and asking legal questions! Hugging Face AI analysis is always enabled for expert legal guidance, and everything is automatically cleared when you're done to maintain confidentiality.**

**🤖 Powered by Hugging Face**: Access to state-of-the-art language models for superior legal analysis.

**Remember: This tool provides legal information, not legal advice. Always consult with a qualified attorney for specific legal matters.**