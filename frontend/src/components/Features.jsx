// src/components/Features.jsx
import React from 'react';

const Features = () => {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <h2 className="text-3xl font-semibold text-gray-800">Features</h2>
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-10">
          <div className="p-6 bg-blue-50 rounded-lg shadow-md">
            <h3 className="text-2xl font-semibold text-blue-600">AI Scoring</h3>
            <p className="mt-4 text-gray-600">Instantly evaluate answers with advanced AI</p>
          </div>
          <div className="p-6 bg-blue-50 rounded-lg shadow-md">
            <h3 className="text-2xl font-semibold text-blue-600">OCR Extraction</h3>
            <p className="mt-4 text-gray-600">Extract text from scanned handwritten responses</p>
          </div>
          <div className="p-6 bg-blue-50 rounded-lg shadow-md">
            <h3 className="text-2xl font-semibold text-blue-600">Manual Review</h3>
            <p className="mt-4 text-gray-600">Easily review and adjust scores as needed</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
