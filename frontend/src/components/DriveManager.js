import React, { useState, useEffect } from 'react';

const DriveManager = () => {
  const [folderId, setFolderId] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);
  const [driveStatus, setDriveStatus] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDriveStatus();
    fetchSyncStatus();
  }, []);

  const fetchDriveStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/google-drive/status');
      if (response.ok) {
        const data = await response.json();
        setDriveStatus(data);
      }
    } catch (error) {
      console.error('Error fetching Google Drive status:', error);
    }
  };

  const fetchSyncStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/drive/sync/status');
      if (response.ok) {
        const data = await response.json();
        setSyncStatus(data);
      }
    } catch (error) {
      // Don't log error if Google Drive is not connected
      console.debug('Sync status not available (Google Drive not connected)');
    }
  };

  const connectToGoogleDrive = async () => {
    setIsConnecting(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/google-drive/connect', {
        method: 'POST',
      });

      const data = await response.json();

      if (response.ok) {
        alert(data.message);
        await fetchDriveStatus();
        await fetchSyncStatus();
      } else {
        setError(data.detail || 'Failed to connect to Google Drive');
      }
    } catch (error) {
      console.error('Error connecting to Google Drive:', error);
      setError('Error connecting to server. Make sure the backend is running.');
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectFromGoogleDrive = async () => {
    if (!window.confirm('Are you sure you want to disconnect from Google Drive? You will need to re-authenticate to use Google Drive features again.')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/google-drive/disconnect', {
        method: 'POST',
      });

      const data = await response.json();

      if (response.ok) {
        alert(data.message);
        await fetchDriveStatus();
        setSyncStatus(null);
        setScanResults(null);
      } else {
        setError(data.detail || 'Failed to disconnect from Google Drive');
      }
    } catch (error) {
      console.error('Error disconnecting from Google Drive:', error);
      setError('Error connecting to server.');
    }
  };

  const scanFolder = async () => {
    if (!folderId.trim() && !window.confirm('Scan entire Google Drive for PDF files? This may take a while.')) {
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

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="drive-manager">
      <h3>PDF Folder Sync Manager</h3>
      
      {/* Google Drive Connection Status */}
      <div className="connection-status">
        <h4>Google Drive Connection</h4>
        {driveStatus && (
          <div className={`status-indicator ${driveStatus.authenticated ? 'connected' : 'disconnected'}`}>
            <span className="status-icon">
              {driveStatus.authenticated ? '✅' : '❌'}
            </span>
            <span className="status-text">{driveStatus.message}</span>
          </div>
        )}
        
        <div className="connection-actions">
          {driveStatus?.authenticated ? (
            <button 
              onClick={disconnectFromGoogleDrive}
              className="disconnect-button"
            >
              🔌 Disconnect Google Drive
            </button>
          ) : (
            <button 
              onClick={connectToGoogleDrive}
              disabled={isConnecting || !driveStatus?.credentials_available}
              className="connect-button"
            >
              {isConnecting ? 'Connecting...' : '🔗 Connect to Google Drive'}
            </button>
          )}
        </div>

        {!driveStatus?.credentials_available && (
          <div className="credentials-warning">
            <p>⚠️ Google Drive credentials not found. To use Google Drive features:</p>
            <ol>
              <li>Set up Google Drive API credentials in Google Cloud Console</li>
              <li>Download credentials.json and place it in the backend directory</li>
              <li>Restart the backend server</li>
            </ol>
          </div>
        )}
      </div>

      {/* Folder Management - Only show if connected */}
      {driveStatus?.authenticated && (
        <>
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
                {isScanning ? 'Scanning...' : 'Scan for PDFs'}
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
            }
          </div>

          {syncStatus && (
            <div className="sync-status">
              <h4>Sync Status</h4>
              <p>PDF Documents Synced: {syncStatus.synced_documents_count}</p>
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
              <p>Found {scanResults.total_documents} PDF documents in {folderId || 'entire Drive'}</p>
              <p>Total Size: {scanResults.total_size_mb} MB</p>
              
              {scanResults.documents.length > 0 && (
                <div className="document-preview">
                  <h5>PDF Documents (showing first {scanResults.showing_first}):</h5>
                  <ul>
                    {scanResults.documents.map((doc) => (
                      <li key={doc.id}>
                        <div className="doc-info">
                          <span className="doc-title">{doc.title}</span>
                          <span className="doc-id">ID: {doc.id}</span>
                          <span className="doc-size">Size: {formatFileSize(doc.size)}</span>
                          {doc.modified_time && (
                            <span className="doc-modified">
                              Modified: {new Date(doc.modified_time).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                        <a href={doc.url} target="_blank" rel="noopener noreferrer" className="doc-link">
                          View
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="sync-actions">
                <p>Ready to sync these PDF documents to your knowledge base?</p>
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
        </>
      )}

      <div className="instructions">
        <h4>How to use PDF Folder Sync:</h4>
        <ol>
          <li><strong>Connect:</strong> Click "Connect to Google Drive" to authenticate (one-time setup)</li>
          <li><strong>Scan:</strong> Preview PDF documents in a folder without adding them</li>
          <li><strong>Quick Sync:</strong> Add only new or updated PDF documents</li>
          <li><strong>Full Sync:</strong> Re-process all PDF documents (slower but thorough)</li>
          <li><strong>Auto-sync:</strong> Automatically sync if enough time has passed</li>
        </ol>
        
        <h5>Folder ID:</h5>
        <p>Get the folder ID from a Google Drive URL:</p>
        <code>https://drive.google.com/drive/folders/[FOLDER_ID]</code>
        <p>Leave empty to scan your entire Google Drive for PDF files.</p>
        
        <h5>Supported Files:</h5>
        <p>Only PDF documents will be processed. Other file types will be ignored.</p>
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

        .connection-status {
          background-color: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 20px;
          border: 1px solid #dee2e6;
        }

        .connection-status h4 {
          margin-top: 0;
          margin-bottom: 10px;
          color: #333;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 15px;
          padding: 10px;
          border-radius: 6px;
        }

        .status-indicator.connected {
          background-color: #d4edda;
          color: #155724;
          border: 1px solid #c3e6cb;
        }

        .status-indicator.disconnected {
          background-color: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }

        .status-icon {
          font-size: 1.2em;
        }

        .status-text {
          font-weight: 500;
        }

        .connection-actions {
          margin-bottom: 15px;
        }

        .connect-button {
          background-color: #28a745;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
        }

        .connect-button:hover:not(:disabled) {
          background-color: #218838;
        }

        .connect-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .disconnect-button {
          background-color: #dc3545;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
        }

        .disconnect-button:hover {
          background-color: #c82333;
        }

        .credentials-warning {
          background-color: #fff3cd;
          color: #856404;
          padding: 12px;
          border-radius: 6px;
          border: 1px solid #ffeaa7;
        }

        .credentials-warning p {
          margin: 0 0 10px 0;
          font-weight: 600;
        }

        .credentials-warning ol {
          margin: 0;
          padding-left: 20px;
          font-size: 0.9em;
        }

        .credentials-warning li {
          margin-bottom: 5px;
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
          color: #d32f2f;
        }

        .doc-id, .doc-modified, .doc-size {
          font-size: 0.8em;
          color: #666;
        }

        .doc-size {
          color: #1976d2;
          font-weight: 500;
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