// src/components/HowItWorks.jsx
import React from 'react';

const HowItWorks = () => {
  return (
    <section className="bg-gray-100 py-16">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <h2 className="text-3xl font-semibold text-gray-800">How It Works</h2>
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-blue-600">1. Upload Exams</h3>
            <p className="mt-4 text-gray-600">Upload scanned exams in any format.</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-blue-600">2. AI Grades</h3>
            <p className="mt-4 text-gray-600">Our AI will grade the exam instantly.</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-blue-600">3. Export Feedback</h3>
            <p className="mt-4 text-gray-600">Download results and feedback for your students.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
