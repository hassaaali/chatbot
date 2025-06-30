import React, { useState, useEffect } from 'react';
import FileUploadManager from './FileUploadManager';

const DocumentManager = () => {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
    
    // Clear cache when component unmounts
    return () => {
      clearCacheOnUnmount();
    };
  }, []);

  const clearCacheOnUnmount = async () => {
    try {
      await fetch('http://localhost:8000/documents/clear', {
        method: 'DELETE',
      });
      console.log('Cache cleared on component unmount');
    } catch (error) {
      console.warn('Could not clear cache on unmount:', error);
    }
  };

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

  const handleUploadSuccess = (documentInfo) => {
    setDocuments(prev => [...prev, documentInfo]);
    fetchStats();
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

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="document-manager">
      <h3>PDF Document Manager</h3>
      
      <div className="cache-info">
        <div className="cache-indicator">
          <span className="cache-icon">🗑️</span>
          <span className="cache-text">Auto-clear on close</span>
        </div>
        <p className="cache-description">
          Documents are automatically cleared when you close the application to keep your system clean.
        </p>
      </div>
      
      <FileUploadManager onUploadSuccess={handleUploadSuccess} />

      {stats && (
        <div className="stats">
          <h4>Knowledge Base Stats</h4>
          <p>Total Documents: {stats.vector_store_stats?.total_documents || 0}</p>
          <p>Total Chunks: {stats.vector_store_stats?.total_chunks || 0}</p>
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
        <h4>Uploaded Documents</h4>
        {documents.length === 0 ? (
          <p>No PDF documents uploaded yet.</p>
        ) : (
          <ul>
            {documents.map((doc) => (
              <li key={doc.document_id}>
                <div className="doc-info">
                  <span className="doc-title">{doc.title}</span>
                  <span className="doc-id">ID: {doc.document_id}</span>
                  <span className="doc-length">Content: {doc.content_length} chars</span>
                  {doc.file_size && (
                    <span className="doc-size">Size: {formatFileSize(doc.file_size)}</span>
                  )}
                  <span className="doc-source source-upload">
                    Source: 📁 Upload
                  </span>
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

        .cache-info {
          background: linear-gradient(135deg, #fff3cd, #ffeaa7);
          border: 1px solid #ffc107;
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 20px;
        }

        .cache-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 6px;
        }

        .cache-icon {
          font-size: 1.2em;
        }

        .cache-text {
          font-weight: 600;
          color: #856404;
        }

        .cache-description {
          margin: 0;
          font-size: 0.85em;
          color: #856404;
          line-height: 1.4;
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
          color: #d32f2f;
        }

        .doc-id, .doc-length, .doc-size {
          font-size: 0.8em;
          color: #666;
        }

        .doc-size {
          color: #1976d2;
          font-weight: 500;
        }

        .doc-source {
          font-size: 0.8em;
          font-weight: 600;
          padding: 2px 6px;
          border-radius: 3px;
          margin-top: 4px;
          display: inline-block;
          width: fit-content;
        }

        .source-upload {
          background-color: #e3f2fd;
          color: #1976d2;
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