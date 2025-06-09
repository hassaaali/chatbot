import React, { useState, useEffect } from 'react';

const DocumentManager = () => {
  const [documentId, setDocumentId] = useState('');
  const [title, setTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState(null);

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
      setMessage('Please enter a document ID');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/documents/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: documentId,
          title: title || undefined
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ ${data.message}`);
        setDocumentId('');
        setTitle('');
        fetchStats(); // Refresh stats
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const clearAllDocuments = async () => {
    if (!window.confirm('Are you sure you want to clear all documents?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/documents/clear', {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ ${data.message}`);
        fetchStats(); // Refresh stats
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
      padding: '20px', 
      border: '1px solid #ddd', 
      borderRadius: '8px', 
      marginBottom: '20px',
      backgroundColor: '#f9f9f9'
    }}>
      <h3>📚 Document Management</h3>
      
      <div style={{ marginBottom: '15px' }}>
        <input
          type="text"
          placeholder="Google Doc ID (from URL)"
          value={documentId}
          onChange={(e) => setDocumentId(e.target.value)}
          style={{ 
            width: '300px', 
            padding: '8px', 
            marginRight: '10px',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
          disabled={isLoading}
        />
        <input
          type="text"
          placeholder="Custom title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{ 
            width: '200px', 
            padding: '8px', 
            marginRight: '10px',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
          disabled={isLoading}
        />
        <button 
          onClick={addDocument} 
          disabled={isLoading || !documentId.trim()}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'Adding...' : 'Add Document'}
        </button>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <button 
          onClick={clearAllDocuments} 
          disabled={isLoading}
          style={{
            padding: '8px 16px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            marginRight: '10px'
          }}
        >
          Clear All Documents
        </button>
        <button 
          onClick={fetchStats} 
          disabled={isLoading}
          style={{
            padding: '8px 16px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          Refresh Stats
        </button>
      </div>

      {message && (
        <div style={{ 
          padding: '10px', 
          marginBottom: '15px',
          backgroundColor: message.includes('✅') ? '#d4edda' : '#f8d7da',
          border: `1px solid ${message.includes('✅') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px',
          color: message.includes('✅') ? '#155724' : '#721c24'
        }}>
          {message}
        </div>
      )}

      {stats && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#e9ecef',
          border: '1px solid #ced4da',
          borderRadius: '4px'
        }}>
          <h4>📊 System Stats</h4>
          <p><strong>Total Documents:</strong> {stats.vector_store_stats.total_documents}</p>
          <p><strong>Embedding Model:</strong> {stats.vector_store_stats.embedding_model}</p>
          <p><strong>Chunk Size:</strong> {stats.processor_config.chunk_size} tokens</p>
          <p><strong>Chunk Overlap:</strong> {stats.processor_config.chunk_overlap} tokens</p>
        </div>
      )}

      <div style={{ 
        marginTop: '15px', 
        padding: '10px', 
        backgroundColor: '#fff3cd',
        border: '1px solid #ffeaa7',
        borderRadius: '4px',
        fontSize: '14px'
      }}>
        <strong>💡 How to get Google Doc ID:</strong><br/>
        1. Open your Google Doc<br/>
        2. Copy the ID from the URL: docs.google.com/document/d/<strong>[DOCUMENT_ID]</strong>/edit<br/>
        3. Make sure the document is shared publicly or with your Google account
      </div>
    </div>
  );
};

export default DocumentManager;