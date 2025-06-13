import React, { useState } from 'react';
import './App.css';
import ChatBox from './ChatBox';
import DocumentManager from './components/DocumentManager';
import DriveManager from './components/DriveManager';

function App() {
  const [useRAG, setUseRAG] = useState(false);
  const [activeTab, setActiveTab] = useState('drive'); // 'drive' or 'individual'

  return (
    <div className="App">
      <header className="App-header">
        <h1>RAG-Enhanced Policy Chatbot</h1>
        <p>Upload PDF policy documents and get intelligent answers</p>
      </header>
      <main className="App-main">
        <div className="container">
          <div className="sidebar">
            <div className="tab-selector">
              <button 
                className={activeTab === 'drive' ? 'active' : ''}
                onClick={() => setActiveTab('drive')}
              >
                PDF Folder Sync
              </button>
              <button 
                className={activeTab === 'individual' ? 'active' : ''}
                onClick={() => setActiveTab('individual')}
              >
                Individual PDFs
              </button>
            </div>
            
            {activeTab === 'drive' ? <DriveManager /> : <DocumentManager />}
            
            <div className="rag-toggle">
              <label>
                <input
                  type="checkbox"
                  checked={useRAG}
                  onChange={(e) => setUseRAG(e.target.checked)}
                />
                Use RAG (Policy Document Context)
              </label>
              <p className="rag-description">
                When enabled, the chatbot will use your uploaded policy documents to provide more accurate and contextual answers.
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