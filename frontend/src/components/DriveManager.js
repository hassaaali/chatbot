import React, { useState, useEffect } from 'react';

const DriveManager = () => {
  const [folderId, setFolderId] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSyncStatus();
  }, []);

  const fetchSyncStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/drive/sync/status');
      if (response.ok) {
        const data = await response.json();
        setSyncStatus(data);
      }
    } catch (error) {
      console.error('Error fetching sync status:', error);
    }
  };

  const scanFolder = async () => {
    if (!folderId.trim() && !window.confirm('Scan entire Google Drive? This may take a while.')) {
      return;
    }

    setIsScanning(true);
    setError('');
    setScanResults(null);

    try {
      const url = folderId.trim() 
        ? `http://localhost:8000/drive/scan?folder_id=${encodeURIComponent(folderId.trim())}`
        : 'http://localhost:8000/drive/scan';
      
      const response = await fetch(url, { method: 'POST' });
      const data = await response.json();

      if (response.ok) {
        setScanResults(data);
        setError('');
      } else {
        setError(data.detail || 'Failed to scan folder');
      }
    } catch (error) {
      console.error('Error scanning folder:', error);
      setError('Error connecting to server. Make sure the backend is running.');
    } finally {
      setIsScanning(false);
    }
  };

  const syncFolder = async (forceFullSync = false) => {
    setIsSyncing(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/drive/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          folder_id: folderId.trim() || null,
          force_full_sync: forceFullSync
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(data.message);
        if (data.stats) {
          setScanResults(null); // Clear scan results after successful sync
        }
        fetchSyncStatus(); // Refresh sync status
      } else {
        setError(data.detail || 'Failed to sync folder');
      }
    } catch (error) {
      console.error('Error syncing folder:', error);
      setError('Error connecting to server. Make sure the backend is running.');
    } finally {
      setIsSyncing(false);
    }
  };

  const triggerAutoSync = async () => {
    try {
      const response = await fetch('http://localhost:8000/drive/auto-sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          folder_id: folderId.trim() || null
        }),
      });

      const data = await response.json();
      if (response.ok) {
        alert(data.message);
        fetchSyncStatus();
      } else {
        setError(data.detail || 'Auto-sync failed');
      }
    } catch (error) {
      console.error('Error in auto-sync:', error);
      setError('Error connecting to server.');
    }
  };

  const extractFolderIdFromUrl = (url) => {
    const match = url.match(/\/folders\/([a-zA-Z0-9-_]+)/);
    return match ? match[1] : url;
  };

  const handleFolderIdChange = (e) => {
    const value = e.target.value;
    const extractedId = extractFolderIdFromUrl(value);
    setFolderId(extractedId);
  };

  return (
    <div className="drive-manager">
      <h3>Google Drive Manager</h3>
      
      <div className="folder-input">
        <input
          type="text"
          value={folderId}
          onChange={handleFolderIdChange}
          placeholder="Google Drive Folder ID or URL (leave empty for entire Drive)"
          disabled={isScanning || isSyncing}
        />
        <div className="button-group">
          <button 
            onClick={scanFolder} 
            disabled={isScanning || isSyncing}
            className="scan-button"
          >
            {isScanning ? 'Scanning...' : 'Scan Folder'}
          </button>
          <button 
            onClick={() => syncFolder(false)} 
            disabled={isScanning || isSyncing}
            className="sync-button"
          >
            {isSyncing ? 'Syncing...' : 'Quick Sync'}
          </button>
          <button 
            onClick={() => syncFolder(true)} 
            disabled={isScanning || isSyncing}
            className="full-sync-button"
          >
            Full Sync
          </button>
        </div>
        {error && <div className="error">{error}</div>}
      </div>

      {syncStatus && (
        <div className="sync-status">
          <h4>Sync Status</h4>
          <p>Documents Synced: {syncStatus.synced_documents_count}</p>
          <p>Last Sync: {syncStatus.last_sync_time ? new Date(syncStatus.last_sync_time).toLocaleString() : 'Never'}</p>
          <p>Auto-sync Interval: {syncStatus.sync_interval_hours} hours</p>
          {syncStatus.should_sync && (
            <div>
              <p className="sync-needed">⚠️ Auto-sync recommended</p>
              <button onClick={triggerAutoSync} className="auto-sync-button">
                Trigger Auto-Sync
              </button>
            </div>
          )}
        </div>
      )}

      {scanResults && (
        <div className="scan-results">
          <h4>Scan Results</h4>
          <p>Found {scanResults.total_documents} documents in {folderId || 'entire Drive'}</p>
          
          {scanResults.documents.length > 0 && (
            <div className="document-preview">
              <h5>Documents (showing first {scanResults.showing_first}):</h5>
              <ul>
                {scanResults.documents.map((doc) => (
                  <li key={doc.id}>
                    <div className="doc-info">
                      <span className="doc-title">{doc.title}</span>
                      <span className="doc-id">ID: {doc.id}</span>
                      {doc.modified_time && (
                        <span className="doc-modified">
                          Modified: {new Date(doc.modified_time).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <a href={doc.url} target="_blank" rel="noopener noreferrer" className="doc-link">
                      Open
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="sync-actions">
            <p>Ready to sync these documents to your knowledge base?</p>
            <button 
              onClick={() => syncFolder(false)} 
              disabled={isSyncing}
              className="sync-button"
            >
              Sync New/Updated Only
            </button>
            <button 
              onClick={() => syncFolder(true)} 
              disabled={isSyncing}
              className="full-sync-button"
            >
              Force Full Sync
            </button>
          </div>
        </div>
      )}

      <div className="instructions">
        <h4>How to use Drive Manager:</h4>
        <ol>
          <li><strong>Scan:</strong> Preview documents in a folder without adding them</li>
          <li><strong>Quick Sync:</strong> Add only new or updated documents</li>
          <li><strong>Full Sync:</strong> Re-process all documents (slower but thorough)</li>
          <li><strong>Auto-sync:</strong> Automatically sync if enough time has passed</li>
        </ol>
        
        <h5>Folder ID:</h5>
        <p>Get the folder ID from a Google Drive URL:</p>
        <code>https://drive.google.com/drive/folders/[FOLDER_ID]</code>
        <p>Leave empty to scan your entire Google Drive.</p>
      </div>

      <style jsx>{`
        .drive-manager {
          background-color: white;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .drive-manager h3 {
          margin-top: 0;
          color: #333;
        }

        .folder-input {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-bottom: 20px;
        }

        .folder-input input {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .button-group {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .button-group button {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .scan-button {
          background-color: #17a2b8;
          color: white;
        }

        .scan-button:hover:not(:disabled) {
          background-color: #138496;
        }

        .sync-button {
          background-color: #28a745;
          color: white;
        }

        .sync-button:hover:not(:disabled) {
          background-color: #218838;
        }

        .full-sync-button {
          background-color: #ffc107;
          color: #212529;
        }

        .full-sync-button:hover:not(:disabled) {
          background-color: #e0a800;
        }

        .auto-sync-button {
          background-color: #6f42c1;
          color: white;
          padding: 6px 12px;
          font-size: 12px;
        }

        .auto-sync-button:hover:not(:disabled) {
          background-color: #5a32a3;
        }

        button:disabled {
          background-color: #ccc !important;
          cursor: not-allowed;
        }

        .error {
          color: #dc3545;
          font-size: 0.9em;
          padding: 8px;
          background-color: #f8d7da;
          border-radius: 4px;
        }

        .sync-status {
          background-color: #f8f9fa;
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .sync-status h4 {
          margin-top: 0;
          margin-bottom: 8px;
        }

        .sync-status p {
          margin: 4px 0;
          font-size: 0.9em;
        }

        .sync-needed {
          color: #856404;
          background-color: #fff3cd;
          padding: 4px 8px;
          border-radius: 4px;
          font-weight: bold;
        }

        .scan-results {
          background-color: #e9ecef;
          padding: 15px;
          border-radius: 4px;
          margin-bottom: 20px;
        }

        .scan-results h4, .scan-results h5 {
          margin-top: 0;
        }

        .document-preview ul {
          list-style: none;
          padding: 0;
          max-height: 300px;
          overflow-y: auto;
        }

        .document-preview li {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px;
          background-color: white;
          margin-bottom: 4px;
          border-radius: 4px;
          font-size: 0.9em;
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

        .doc-id, .doc-modified {
          font-size: 0.8em;
          color: #666;
        }

        .doc-link {
          color: #007bff;
          text-decoration: none;
          font-size: 0.8em;
          padding: 4px 8px;
          border: 1px solid #007bff;
          border-radius: 4px;
        }

        .doc-link:hover {
          background-color: #007bff;
          color: white;
        }

        .sync-actions {
          margin-top: 15px;
          padding-top: 15px;
          border-top: 1px solid #ccc;
        }

        .sync-actions p {
          margin-bottom: 10px;
          font-weight: bold;
        }

        .instructions {
          margin-top: 20px;
          padding-top: 15px;
          border-top: 1px solid #ddd;
        }

        .instructions h4, .instructions h5 {
          margin-bottom: 8px;
          color: #333;
        }

        .instructions ol, .instructions p {
          font-size: 0.9em;
          color: #666;
        }

        .instructions ol {
          padding-left: 20px;
        }

        .instructions li {
          margin-bottom: 4px;
        }

        .instructions code {
          background-color: #f8f9fa;
          padding: 2px 4px;
          border-radius: 3px;
          font-family: monospace;
          font-size: 0.8em;
        }
      `}</style>
    </div>
  );
};

export default DriveManager;