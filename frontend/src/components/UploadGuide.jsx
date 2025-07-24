import React, { useState } from 'react';
import api from '../services/api'; // Correct import

const UploadGuide = () => {
  const [file, setFile] = useState(null);
  const [testId, setTestId] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setUploadStatus('');
  };

  const handleUpload = async () => {
    if (!file || !testId) {
      setUploadStatus('Please select a file and enter Test ID.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);         // 👈 Matches request.files['file']
    formData.append('test_id', testId);    // 👈 Matches request.form['test_id']

    try {
      setUploadStatus('Uploading...');
      const response = await api.post('/teacher/upload_script', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadStatus('Upload successful!');
      setFile(null);
      setTestId('');
    } catch (error) {
      setUploadStatus('Upload failed. Please try again.');
      console.error(error);
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Upload Guide</h2>
      <p className="mb-2">Accepted formats: PDF, DOCX</p>

      <input
        type="file"
        onChange={handleFileChange}
        className="mb-2"
        accept=".pdf,.docx"
      />

      <input
        type="text"
        placeholder="Enter Test ID"
        value={testId}
        onChange={(e) => setTestId(e.target.value)}
        className="mb-4 block w-full border px-2 py-1"
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
