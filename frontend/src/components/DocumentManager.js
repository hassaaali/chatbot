import React, { useState, useEffect } from 'react';

const DocumentManager = () => {
  const [documentId, setDocumentId] = useState('');
  const [title, setTitle] = useState('');
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/documents/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const addDocument = async () => {
    if (!documentId.trim()) {
      setError('Please enter a Google Doc ID');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/documents/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          document_id: documentId.trim(),
          title: title.trim() || null
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setDocuments(prev => [...prev, data.document_info]);
        setDocumentId('');
        setTitle('');
        fetchStats();
        setError('');
        alert(`Document "${data.document_info.title}" added successfully!`);
      } else {
        setError(data.detail || 'Failed to add document');
      }
    } catch (error) {
      console.error('Error adding document:', error);
      setError('Error connecting to server. Make sure the backend is running on http://localhost:8000');
    } finally {
      setIsLoading(false);
    }
  };

  const removeDocument = async (docId) => {
    try {
      const response = await fetch(`http://localhost:8000/documents/${docId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setDocuments(prev => prev.filter(doc => doc.document_id !== docId));
        fetchStats();
        alert('Document removed successfully!');
      } else {
        const data = await response.json();
        alert(`Error: ${data.detail || 'Failed to remove document'}`);
      }
    } catch (error) {
      console.error('Error removing document:', error);
      alert('Error removing document. Please try again.');
    }
  };

  const clearAllDocuments = async () => {
    if (!window.confirm('Are you sure you want to clear all documents?')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/documents/clear', {
        method: 'DELETE',
      });

      if (response.ok) {
        setDocuments([]);
        fetchStats();
        alert('All documents cleared successfully!');
      } else {
        const data = await response.json();
        alert(`Error: ${data.detail || 'Failed to clear documents'}`);
      }
    } catch (error) {
      console.error('Error clearing documents:', error);
      alert('Error clearing documents. Please try again.');
    }
  };

  const extractDocIdFromUrl = (url) => {
    const match = url.match(/\/document\/d\/([a-zA-Z0-9-_]+)/);
    return match ? match[1] : url;
  };

  const handleDocumentIdChange = (e) => {
    const value = e.target.value;
    const extractedId = extractDocIdFromUrl(value);
    setDocumentId(extractedId);
  };

  return (
    <div className="document-manager">
      <h3>Document Manager</h3>
      
      <div className="add-document">
        <input
          type="text"
          value={documentId}
          onChange={handleDocumentIdChange}
          placeholder="Google Doc ID or URL"
          disabled={isLoading}
        />
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Custom title (optional)"
          disabled={isLoading}
        />
        <button onClick={addDocument} disabled={isLoading || !documentId.trim()}>
          {isLoading ? 'Adding...' : 'Add Document'}
        </button>
        {error && <div className="error">{error}</div>}
        }
      </div>

      {stats && (
        <div className="stats">
          <h4>Knowledge Base Stats</h4>
          <p>Total Documents: {stats.vector_store_stats?.total_documents || 0}</p>
          <p>Embedding Model: {stats.vector_store_stats?.embedding_model || 'N/A'}</p>
          {stats.vector_store_stats?.sources && (
            <div>
              <p>Sources:</p>
              <ul>
                {Object.entries(stats.vector_store_stats.sources).map(([source, count]) => (
                  <li key={source}>{source}: {count} chunks</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="document-list">
        <h4>Added Documents</h4>
        {documents.length === 0 ? (
          <p>No documents added yet.</p>
        ) : (
          <ul>
            {documents.map((doc) => (
              <li key={doc.document_id}>
                <div className="doc-info">
                  <span className="doc-title">{doc.title}</span>
                  <span className="doc-id">ID: {doc.document_id}</span>
                  <span className="doc-length">Length: {doc.content_length} chars</span>
                </div>
                <button onClick={() => removeDocument(doc.document_id)}>Remove</button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {documents.length > 0 && (
        <button className="clear-all" onClick={clearAllDocuments}>
          Clear All Documents
        </button>
      )}

      <div className="instructions">
        <h4>How to add a Google Doc:</h4>
        <ol>
          <li>Open your Google Doc</li>
          <li>Make sure it's shared (at least view access)</li>
          <li>Copy the document ID from the URL or paste the full URL</li>
          <li>Optionally add a custom title</li>
          <li>Click "Add Document"</li>
        </ol>
      </div>

      <style jsx>{`
        .document-manager {
          background-color: white;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .document-manager h3 {
          margin-top: 0;
          color: #333;
        }

        .add-document {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-bottom: 20px;
        }

        .add-document input {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .add-document button {
          padding: 8px 16px;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .add-document button:hover:not(:disabled) {
          background-color: #218838;
        }

        .add-document button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .error {
          color: #dc3545;
          font-size: 0.9em;
          padding: 5px;
          background-color: #f8d7da;
          border-radius: 4px;
        }

        .stats {
          background-color: #f8f9fa;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .stats h4 {
          margin-top: 0;
          margin-bottom: 10px;
        }

        .stats p {
          margin: 5px 0;
          font-size: 0.9em;
        }

        .stats ul {
          margin: 5px 0;
          padding-left: 20px;
          font-size: 0.8em;
        }

        .document-list h4 {
          margin-bottom: 10px;
        }

        .document-list ul {
          list-style: none;
          padding: 0;
        }

        .document-list li {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background-color: #f8f9fa;
          margin-bottom: 8px;
          border-radius: 4px;
        }

        .doc-info {
          display: flex;
          flex-direction: column;
          flex: 1;
        }

        .doc-title {
          font-weight: bold;
          margin-bottom: 2px;
        }

        .doc-id, .doc-length {
          font-size: 0.8em;
          color: #666;
        }

        .document-list button {
          padding: 4px 8px;
          background-color: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.8em;
        }

        .document-list button:hover {
          background-color: #c82333;
        }

        .clear-all {
          width: 100%;
          padding: 10px;
          background-color: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 15px;
        }

        .clear-all:hover {
          background-color: #c82333;
        }

        .instructions {
          margin-top: 20px;
          padding-top: 15px;
          border-top: 1px solid #ddd;
        }

        .instructions h4 {
          margin-bottom: 10px;
          color: #333;
        }

        .instructions ol {
          font-size: 0.9em;
          color: #666;
          padding-left: 20px;
        }

        .instructions li {
          margin-bottom: 5px;
        }
      `}</style>
    </div>
  );
};

export default DocumentManager;