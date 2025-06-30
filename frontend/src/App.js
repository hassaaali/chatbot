import React, { useEffect } from 'react';
import './App.css';
import ChatBox from './ChatBox';
import DocumentManager from './components/DocumentManager';

function App() {
  useEffect(() => {
    // Function to clear cache when the application is closed
    const clearCacheOnClose = async () => {
      try {
        // Clear all documents from the backend
        await fetch('http://localhost:8000/documents/clear', {
          method: 'DELETE',
        });
        console.log('Cache cleared successfully');
      } catch (error) {
        console.warn('Could not clear cache on close:', error);
      }
    };

    // Handle browser/tab close events
    const handleBeforeUnload = (event) => {
      // Clear cache when user closes the tab/browser
      clearCacheOnClose();
      
      // Optional: Show confirmation dialog (some browsers may ignore this)
      event.preventDefault();
      event.returnValue = '';
    };

    // Handle page visibility change (when user switches tabs or minimizes)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        // Clear cache when page becomes hidden
        clearCacheOnClose();
      }
    };

    // Handle browser back/forward navigation
    const handlePopState = () => {
      clearCacheOnClose();
    };

    // Add event listeners
    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('popstate', handlePopState);

    // Cleanup function to remove event listeners
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('popstate', handlePopState);
      
      // Final cleanup when component unmounts
      clearCacheOnClose();
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>⚖️ Legal AI Assistant</h1>
        <p>Upload legal documents and get expert legal analysis and guidance</p>
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