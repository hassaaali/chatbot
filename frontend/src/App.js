import React from 'react';
import './App.css';
import ChatBox from './ChatBox';
import DocumentManager from './components/DocumentManager';

function App() {
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
          </div>
          <div className="chat-container">
            <ChatBox />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;