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
      <h2>Document Manager</h2>
      
      <div className="add-document">
        <h3>Add Google Doc</h3>
        <input
          type="text"
          value={documentId}
          onChange={(e) => setDocumentId(e.target.value)}
          placeholder="Enter Google Doc ID"
          disabled={isLoading}
        />
        <button onClick={addDocument} disabled={isLoading || !documentId.trim()}>
          {isLoading ? 'Adding...' : 'Add Document'}
        </button>
      </div>

      {stats && (
        <div className="stats">
          <h3>Statistics</h3>
          <p>Total Documents: {stats.total_documents}</p>
          <p>Total Chunks: {stats.total_chunks}</p>
        </div>
      )}

      <div className="document-list">
        <h3>Added Documents</h3>
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
        <div className="clear-all">
          <button onClick={clearAllDocuments} className="danger">
            Clear All Documents
          </button>
        </div>
      )}

      <style jsx>{`
        .document-manager {
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .document-manager h2 {
          margin-top: 0;
          color: #333;
          border-bottom: 2px solid #007bff;
          padding-bottom: 10px;
        }

        .add-document {
          margin-bottom: 20px;
        }

        .add-document h3 {
          margin-bottom: 10px;
          color: #555;
        }

        .add-document input {
          width: 100%;
          padding: 8px;
          margin-bottom: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .add-document button {
          width: 100%;
          padding: 10px;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .add-document button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }

        .add-document button:hover:not(:disabled) {
          background-color: #218838;
        }

        .stats {
          background-color: #f8f9fa;
          padding: 15px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .stats h3 {
          margin-top: 0;
          color: #555;
        }

        .stats p {
          margin: 5px 0;
          color: #666;
        }

        .document-list {
          flex: 1;
          overflow-y: auto;
        }

        .document-list h3 {
          color: #555;
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
          border: 1px solid #ddd;
          border-radius: 4px;
          margin-bottom: 5px;
          background-color: #f8f9fa;
        }

        .document-list button {
          background-color: #dc3545;
          color: white;
          border: none;
          padding: 5px 10px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9em;
        }

        .document-list button:hover {
          background-color: #c82333;
        }

        .clear-all {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #ddd;
        }

        .clear-all button.danger {
          width: 100%;
          padding: 10px;
          background-color: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .clear-all button.danger:hover {
          background-color: #c82333;
        }
      `}</style>
    </div>
  );
};

export default DocumentManager;