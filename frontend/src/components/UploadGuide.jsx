import api from '../services/api';
import React, { useState } from 'react';
import axios from '../services/api';

const UploadGuide = () => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setUploadStatus('');
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadStatus('Uploading...');
      const response = await api.('/api/student/upload-guide', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadStatus('Upload successful!');
      setFile(null);
    } catch (error) {
      setUploadStatus('Upload failed. Please try again.');
      console.error(error);
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Upload Guide</h2>
      <p className="mb-4">
        Please upload your marking guide here. Accepted formats: PDF, DOCX.
      </p>

      <input
        type="file"
        onChange={handleFileChange}
        className="mb-4"
        accept=".pdf,.docx"
      />

      <button
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Upload
      </button>

      {uploadStatus && (
        <p className="mt-2 text-sm text-gray-700">{uploadStatus}</p>
      )}
    </div>
  );
};

export default UploadGuide;


