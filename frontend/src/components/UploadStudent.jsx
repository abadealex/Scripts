import React, { useState } from 'react';
import axios from '../api';

const UploadStudent = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('/student/upload', formData);
      alert('Uploaded successfully');
    } catch (err) {
      alert('Upload failed');
    }
    setUploading(false);
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">Upload Student Answer</h2>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={uploading} className="ml-2 px-4 py-1 bg-blue-600 text-white rounded">
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
};

export default UploadStudent;
