# RAG-Enhanced Chatbot

A comprehensive RAG (Retrieval-Augmented Generation) chatbot that integrates with Google Docs to provide context-aware responses based on your document content.

## Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── services/           # Core services (Google Docs, RAG, Vector Store)
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

1. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure environment:**
   - Copy `backend/.env.example` to `backend/.env`
   - Add your Together AI API key
   - Set up Google Docs API credentials (see setup_instructions.md)

### Running the Application

1. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```

2. **Start the frontend (in a new terminal):**
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Features

- **Document Integration**: Add Google Docs to your knowledge base
- **RAG Pipeline**: Context-aware responses using document content
- **Streaming Chat**: Real-time streaming responses
- **Vector Search**: Semantic similarity search using embeddings
- **Document Management**: Add, remove, and manage documents
- **Statistics Dashboard**: View system statistics and document info

## API Endpoints

- `POST /documents/add` - Add Google Doc to knowledge base
- `DELETE /documents/{id}` - Remove document
- `GET /documents/stats` - View system statistics
- `DELETE /documents/clear` - Clear all documents
- `POST /chat/stream` - Chat with RAG enhancement

## Usage

1. **Add Documents**: Use the Document Manager to add Google Docs by ID
2. **Enable RAG**: Toggle "Use RAG" to enable context-aware responses
3. **Chat**: Ask questions related to your uploaded documents
4. **View Sources**: See which documents the chatbot references

For detailed setup instructions, see `setup_instructions.md`.