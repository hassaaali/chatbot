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
        <h1>RAG-Enhanced Chatbot</h1>
      </header>
      <main className="App-main">
        <div className="container">
          <div className="sidebar">
            <div className="tab-selector">
              <button 
                className={activeTab === 'drive' ? 'active' : ''}
                onClick={() => setActiveTab('drive')}
              >
                Drive Sync
              </button>
              <button 
                className={activeTab === 'individual' ? 'active' : ''}
                onClick={() => setActiveTab('individual')}
              >
                Individual Docs
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
                Use RAG (Document Context)
              </label>
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