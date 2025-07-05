// src/components/BulkUploadForm.jsx
import React, { useState } from 'react';
import styles from '../styles/components/BulkUploadForm.module.css';
import api from '../services/api';

const BulkUploadForm = () => {
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    const formData = new FormData();
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
    } catch (error) {
      alert('Upload failed.');
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={styles.uploadForm}>
      <h2>Bulk Upload Student Scripts</h2>
      <input
        type="file"
        className={styles.fileInput}
        multiple
        accept=".zip,image/*,application/pdf"
        onChange={handleFileChange}
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
