import React from 'react';
import ChatBox from './ChatBox';
import DocumentManager from './components/DocumentManager';

function App() {
  return (
    <div className="App" style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', color: '#333', marginBottom: '30px' }}>
        🤖 RAG-Enhanced AI Chatbot
      </h1>
      <DocumentManager />
      <ChatBox />
    </div>
  );
}

export default App;