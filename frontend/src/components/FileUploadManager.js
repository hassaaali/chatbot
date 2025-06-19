import React, { useState } from 'react';

const FileUploadManager = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [title, setTitle] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (file) => {
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setTitle(file.name.replace('.pdf', ''));
      setError('');
    } else {
      setError('Please select a PDF file');
      setSelectedFile(null);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file');
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (title.trim()) {
        formData.append('title', title.trim());
      }

      const response = await fetch('http://localhost:8000/documents/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setSelectedFile(null);
        setTitle('');
        setError('');
        alert(`PDF "${data.document_info.title}" uploaded successfully!`);
        
        // Reset file input
        const fileInput = document.getElementById('pdf-file-input');
        if (fileInput) fileInput.value = '';
        
        // Notify parent component
        if (onUploadSuccess) {
          onUploadSuccess(data.document_info);
        }
      } else {
        setError(data.detail || 'Failed to upload PDF');
      }
    } catch (error) {
      console.error('Error uploading PDF:', error);
      setError('Error connecting to server. Make sure the backend is running on http://localhost:8000');
    } finally {
      setIsUploading(false);
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
    <div className="file-upload-manager">
      <h4>Upload PDF File</h4>
      
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          <div className="upload-icon">📄</div>
          <p>Drag and drop a PDF file here, or click to select</p>
          <input
            id="pdf-file-input"
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            disabled={isUploading}
            style={{ display: 'none' }}
          />
          <button 
            type="button"
            onClick={() => document.getElementById('pdf-file-input').click()}
            disabled={isUploading}
            className="select-file-btn"
          >
            Select PDF File
          </button>
        </div>
      </div>

      {selectedFile && (
        <div className="selected-file">
          <h5>Selected File:</h5>
          <div className="file-info">
            <span className="file-name">{selectedFile.name}</span>
            <span className="file-size">{formatFileSize(selectedFile.size)}</span>
          </div>
          
          <div className="title-input">
            <label htmlFor="file-title">Custom Title (optional):</label>
            <input
              id="file-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter a custom title for this document"
              disabled={isUploading}
            />
          </div>

          <div className="upload-actions">
            <button 
              onClick={uploadFile} 
              disabled={isUploading}
              className="upload-btn"
            >
              {isUploading ? 'Uploading...' : 'Upload PDF'}
            </button>
            <button 
              onClick={() => {
                setSelectedFile(null);
                setTitle('');
                setError('');
                document.getElementById('pdf-file-input').value = '';
              }}
              disabled={isUploading}
              className="cancel-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <div className="upload-info">
        <h5>Upload Requirements:</h5>
        <ul>
          <li>File format: PDF only</li>
          <li>Maximum file size: 50MB</li>
          <li>Text-based PDFs work best (scanned images may have limited text extraction)</li>
          <li>Files are processed locally and added to your knowledge base</li>
        </ul>
      </div>

      <style jsx>{`
        .file-upload-manager {
          background-color: #f8f9fa;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .file-upload-manager h4 {
          margin-top: 0;
          margin-bottom: 15px;
          color: #333;
        }

        .upload-area {
          border: 2px dashed #dee2e6;
          border-radius: 8px;
          padding: 30px;
          text-align: center;
          background-color: white;
          transition: all 0.3s ease;
          cursor: pointer;
        }

        .upload-area:hover {
          border-color: #007bff;
          background-color: #f8f9ff;
        }

        .upload-area.drag-active {
          border-color: #007bff;
          background-color: #e3f2fd;
          transform: scale(1.02);
        }

        .upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 15px;
        }

        .upload-icon {
          font-size: 3rem;
          opacity: 0.6;
        }

        .upload-content p {
          margin: 0;
          color: #6c757d;
          font-size: 1rem;
        }

        .select-file-btn {
          padding: 10px 20px;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: background-color 0.2s;
        }

        .select-file-btn:hover:not(:disabled) {
          background-color: #0056b3;
        }

        .select-file-btn:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .selected-file {
          margin-top: 20px;
          padding: 15px;
          background-color: white;
          border-radius: 6px;
          border: 1px solid #dee2e6;
        }

        .selected-file h5 {
          margin-top: 0;
          margin-bottom: 10px;
          color: #333;
        }

        .file-info {
          display: flex;
          flex-direction: column;
          gap: 5px;
          margin-bottom: 15px;
        }

        .file-name {
          font-weight: bold;
          color: #007bff;
        }

        .file-size {
          font-size: 0.9em;
          color: #6c757d;
        }

        .title-input {
          margin-bottom: 15px;
        }

        .title-input label {
          display: block;
          margin-bottom: 5px;
          font-weight: 600;
          color: #495057;
        }

        .title-input input {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 14px;
          box-sizing: border-box;
        }

        .title-input input:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .upload-actions {
          display: flex;
          gap: 10px;
        }

        .upload-btn {
          padding: 10px 20px;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }

        .upload-btn:hover:not(:disabled) {
          background-color: #218838;
        }

        .upload-btn:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .cancel-btn {
          padding: 10px 20px;
          background-color: #6c757d;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .cancel-btn:hover:not(:disabled) {
          background-color: #5a6268;
        }

        .cancel-btn:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .error {
          margin-top: 15px;
          color: #dc3545;
          font-size: 0.9em;
          padding: 10px;
          background-color: #f8d7da;
          border-radius: 4px;
          border: 1px solid #f5c6cb;
        }

        .upload-info {
          margin-top: 20px;
          padding-top: 15px;
          border-top: 1px solid #dee2e6;
        }

        .upload-info h5 {
          margin-bottom: 10px;
          color: #333;
        }

        .upload-info ul {
          margin: 0;
          padding-left: 20px;
          font-size: 0.9em;
          color: #6c757d;
        }

        .upload-info li {
          margin-bottom: 5px;
        }
      `}</style>
    </div>
  );
};

export default FileUploadManager;