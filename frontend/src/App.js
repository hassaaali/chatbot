import React, { useState } from 'react';
import './App.css';
import ChatBox from './ChatBox';
import DocumentManager from './components/DocumentManager';

function App() {
  const [useRAG, setUseRAG] = useState(false);

  return (
    <div className="App">
      <header className="App-header">
        <h1>RAG-Enhanced PDF Chatbot</h1>
        <p>Upload PDF documents and get intelligent, context-aware answers</p>
      </header>
      <main className="App-main">
        <div className="container">
          <div className="sidebar">
            <DocumentManager />
            
            <div className="rag-toggle">
              <label>
                <input
                  type="checkbox"
                  checked={useRAG}
                  onChange={(e) => setUseRAG(e.target.checked)}
                />
                Use RAG (Document Context)
              </label>
              <p className="rag-description">
                When enabled, the chatbot will use your uploaded PDF documents to provide more accurate and contextual answers.
              </p>
            </div>
          </div>
          <div className="chat-container">
            <ChatBox useRAG={useRAG} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;