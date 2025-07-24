// src/components/HeroSection.jsx
import React from 'react';

const HeroSection = () => {
  return (
    <section className="bg-blue-100 py-16 text-center">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-5xl font-semibold text-gray-800">Automated Grading Made Simple</h2>
        <p className="mt-4 text-xl text-gray-600">Grade papers 10x faster using AI</p>
        <div className="mt-8">
          <a href="/get-started" className="bg-blue-600 text-white py-2 px-6 rounded-lg text-lg mr-4">Get Started</a>
          <a href="#how-it-works" className="bg-transparent border-2 border-blue-600 text-blue-600 py-2 px-6 rounded-lg text-lg">See How It Works</a>
        </div>
        <img src="/assets/images/smart_scripts_logo.png" alt="SmartScripts logo" className="mx-auto mt-8 w-80" />
      </div>
    </section>
  );
};

export default HeroSection;
