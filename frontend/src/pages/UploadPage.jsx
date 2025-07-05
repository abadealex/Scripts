import React from 'react';
import UploadGuide from '../components/UploadGuide';

const UploadPage = () => {
  return (
    <div className="page">
      <h1>Upload</h1>
      <UploadGuide />
      {/* Optionally add UploadStudent or other upload components */}
    </div>
  );
};

export default UploadPage;
