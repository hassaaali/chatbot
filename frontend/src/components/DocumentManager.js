import React, { useState, useEffect } from 'react';

const DocumentManager = () => {
  const [documentId, setDocumentId] = useState('');
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

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
    if (!documentId.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/documents/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ document_id: documentId }),
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(prev => [...prev, data]);
        setDocumentId('');
        fetchStats();
        alert('Document added successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to add document'}`);
      }
    } catch (error) {
      console.error('Error adding document:', error);
      alert('Error adding document. Please try again.');
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
        setDocuments(prev => prev.filter(doc => doc.id !== docId));
        fetchStats();
        alert('Document removed successfully!');
      } else {
        alert('Error removing document');
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
        alert('Error clearing documents');
      }
    } catch (error) {
      console.error('Error clearing documents:', error);
      alert('Error clearing documents. Please try again.');
    }
  };

  return (
    <div className="document-manager">
      <h3>Document Manager</h3>
      
      <div className="add-document">
        <input
          type="text"
          value={documentId}
          onChange={(e) => setDocumentId(e.target.value)}
          placeholder="Google Doc ID"
          disabled={isLoading}
        />
        <button onClick={addDocument} disabled={isLoading || !documentId.trim()}>
          {isLoading ? 'Adding...' : 'Add Document'}
        </button>
      </div>

      {stats && (
        <div className="stats">
          <h4>Knowledge Base Stats</h4>
          <p>Documents: {stats.total_documents}</p>
          <p>Chunks: {stats.total_chunks}</p>
        </div>
      )}

      <div className="document-list">
        <h4>Added Documents</h4>
        {documents.length === 0 ? (
          <p>No documents added yet.</p>
        ) : (
          <ul>
            {documents.map((doc) => (
              <li key={doc.id}>
                <span>{doc.title || doc.id}</span>
                <button onClick={() => removeDocument(doc.id)}>Remove</button>
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
          padding: 8px;
          background-color: #f8f9fa;
          margin-bottom: 5px;
          border-radius: 4px;
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
      `}</style>
    </div>
  );
};

export default DocumentManager;