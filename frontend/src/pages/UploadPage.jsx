import React, { useState } from 'react';
import UploadGuide from '../components/UploadGuide';
import axios from 'axios';

const UploadPage = () => {
  const [files, setFiles] = useState([]);
  const [testId, setTestId] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleTestIdChange = (e) => {
    setTestId(e.target.value);
  };

  const handleUpload = async () => {
    if (!testId) {
      setMessage('Please enter a test ID.');
      return;
    }
    if (files.length === 0) {
      setMessage('Please select at least one file.');
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post(
        `/api/v1/submissions/upload/${testId}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setMessage(response.data.message || 'Upload successful!');
    } catch (error) {
      setMessage(error.response?.data?.error || 'Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="page"
      style={{ maxWidth: 900, margin: '20px auto', padding: 20, fontFamily: 'Arial, sans-serif' }}
    >
      <h1>Upload</h1>
      <UploadGuide />

      <div style={{ marginTop: 20 }}>
        <label>
          Test ID:
          <input
            type="text"
            value={testId}
            onChange={handleTestIdChange}
            style={{ marginLeft: 10, padding: 5 }}
          />
        </label>
      </div>

      <div style={{ marginTop: 20 }}>
        <input type="file" multiple onChange={handleFileChange} />
      </div>

      <div style={{ marginTop: 20 }}>
        <button onClick={handleUpload} disabled={loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </div>

      {message && (
        <div style={{ marginTop: 20, color: message.includes('failed') ? 'red' : 'green' }}>
          {message}
        </div>
      )}
    </div>
  );
};

export default UploadPage;
