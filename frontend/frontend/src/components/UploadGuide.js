// Smartscripts/frontend/src/components/UploadGuide.js
import React, { useState } from "react";

const UploadGuide = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [uploadError, setUploadError] = useState("");

  const handleFileChange = (e) => {
    setUploadError("");
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // Only allow JSON files
    if (!selectedFile.name.match(/\.(json)$/)) {
      setUploadError("Only JSON files are supported.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = () => {
    if (!file) {
      setUploadError("Please select a file to upload.");
      return;
    }
    if (onUpload) onUpload(file);
  };

  return (
    <div className="upload-guide p-3 border rounded">
      <h3>Upload Marking Guide (Rubric)</h3>
      <input type="file" accept=".json" onChange={handleFileChange} />
      {uploadError && <div className="text-danger mt-2">{uploadError}</div>}
      <button
        className="btn btn-primary mt-3"
        onClick={handleUpload}
        disabled={!file}
      >
        Upload
      </button>
    </div>
  );
};

export default UploadGuide;
