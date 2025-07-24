// src/components/BulkUploadForm.jsx
import React, { useState } from 'react';
import styles from '../styles/components/BulkUploadForm.module.css';
import api from '../services/api';

const BulkUploadForm = () => {
  const [files, setFiles] = useState([]);
  const [batchName, setBatchName] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (files.length === 0 || batchName.trim() === '') {
      alert('Please provide a batch name and select files.');
      return;
    }

    const formData = new FormData();
    formData.append('batch_name', batchName);
    files.forEach(file => formData.append('files', file));

    try {
      setUploading(true);
      await api.post('/upload/bulk', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percent);
        },
      });
      alert('Upload successful!');
      setFiles([]);
      setBatchName('');
    } catch (error) {
      alert('Upload failed.');
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={styles.uploadForm}>
      <h2>📁 Bulk Upload Student Scripts</h2>

      <input
        type="text"
        placeholder="Enter Batch Name"
        value={batchName}
        onChange={(e) => setBatchName(e.target.value)}
        className={styles.textInput}
        disabled={uploading}
      />

      <input
        type="file"
        className={styles.fileInput}
        multiple
        accept=".zip,image/*,application/pdf"
        onChange={handleFileChange}
        disabled={uploading}
      />

      <button
        className={styles.uploadButton}
        onClick={handleUpload}
        disabled={uploading}
      >
        {uploading ? 'Uploading...' : 'Upload Files'}
      </button>

      {uploading && (
        <div className={styles.progressBarContainer}>
          <div
            className={styles.progressBar}
            style={{ width: `${uploadProgress}%` }}
          ></div>
        </div>
      )}

      {files.length > 0 && (
        <ul className={styles.fileList}>
          {files.map((file, idx) => (
            <li key={idx} className={styles.fileItem}>
              📄 {file.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default BulkUploadForm;
