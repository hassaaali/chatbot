const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://127.0.0.1:3000'],
  credentials: true
}));
app.use(express.json());

// Mock data store (in production, use a real database)
let documents = [];
let vectorStore = [];

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    services: {
      google_docs: false, // Will be true when properly configured
      rag: true,
      vector_store: true
    }
  });
});

// Document management endpoints
app.post('/documents/add', async (req, res) => {
  try {
    const { document_id, title } = req.body;
    
    if (!document_id) {
      return res.status(400).json({ detail: 'Document ID is required' });
    }

    // Mock document processing (replace with actual Google Docs integration)
    const mockDocument = {
      document_id: document_id,
      title: title || `Document ${document_id}`,
      content_length: Math.floor(Math.random() * 5000) + 1000,
      chunks: Math.floor(Math.random() * 10) + 1
    };

    documents.push(mockDocument);

    res.json({
      success: true,
      message: `Successfully added document '${mockDocument.title}'`,
      document_info: mockDocument
    });
  } catch (error) {
    console.error('Error adding document:', error);
    res.status(500).json({ detail: 'Failed to add document' });
  }
});

app.delete('/documents/:document_id', (req, res) => {
  try {
    const { document_id } = req.params;
    const initialLength = documents.length;
    documents = documents.filter(doc => doc.document_id !== document_id);
    
    if (documents.length < initialLength) {
      res.json({ success: true, message: `Document ${document_id} removed successfully` });
    } else {
      res.status(404).json({ detail: 'Document not found' });
    }
  } catch (error) {
    console.error('Error removing document:', error);
    res.status(500).json({ detail: 'Failed to remove document' });
  }
});

app.get('/documents/stats', (req, res) => {
  try {
    const totalChunks = documents.reduce((sum, doc) => sum + (doc.chunks || 0), 0);
    
    res.json({
      vector_store_stats: {
        total_documents: documents.length,
        embedding_model: 'all-MiniLM-L6-v2',
        sources: {
          google_docs: totalChunks
        }
      },
      processor_config: {
        chunk_size: 1000,
        chunk_overlap: 200
      }
    });
  } catch (error) {
    console.error('Error getting stats:', error);
    res.status(500).json({ detail: 'Failed to get stats' });
  }
});

app.delete('/documents/clear', (req, res) => {
  try {
    documents = [];
    vectorStore = [];
    res.json({ success: true, message: 'All documents cleared successfully' });
  } catch (error) {
    console.error('Error clearing documents:', error);
    res.status(500).json({ detail: 'Failed to clear documents' });
  }
});

// Chat endpoint with streaming
app.post('/chat/stream', async (req, res) => {
  try {
    const { prompt, use_rag } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ detail: 'Prompt is required' });
    }

    // Set up Server-Sent Events
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Cache-Control'
    });

    // Mock streaming response
    if (use_rag && documents.length > 0) {
      const sources = documents.slice(0, 2).map(doc => doc.title);
      res.write(`data: [CONTEXT] Using information from: ${sources.join(', ')}\n\n`);
    }

    // Simulate streaming response
    const mockResponse = use_rag && documents.length > 0 
      ? `Based on the documents you've provided, I can help answer your question about "${prompt}". This is a mock response that demonstrates the RAG functionality. In a full implementation, this would use actual AI models and vector search to provide contextual answers.`
      : `I understand you're asking about "${prompt}". This is a mock response. To enable RAG functionality, please add some Google Docs to the knowledge base and ensure the backend is properly configured with API keys.`;

    // Stream the response word by word
    const words = mockResponse.split(' ');
    for (let i = 0; i < words.length; i++) {
      const word = words[i] + (i < words.length - 1 ? ' ' : '');
      res.write(`data: ${word}\n\n`);
      
      // Add small delay to simulate real streaming
      await new Promise(resolve => setTimeout(resolve, 50));
    }

    res.write('data: [DONE]\n\n');
    res.end();

  } catch (error) {
    console.error('Error in chat stream:', error);
    res.write(`data: [ERROR] Internal server error\n\n`);
    res.end();
  }
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'RAG-Enhanced Chatbot API', 
    version: '1.0.0',
    status: 'running'
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('API endpoints:');
  console.log('  GET  /health - Health check');
  console.log('  POST /documents/add - Add document');
  console.log('  GET  /documents/stats - Get stats');
  console.log('  POST /chat/stream - Chat with streaming');
});