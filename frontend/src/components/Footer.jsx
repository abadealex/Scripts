// src/components/Footer.jsx
import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p>&copy; 2025 SmartScripts. All rights reserved.</p>
        <div className="mt-4 space-x-4">
          <a href="/terms" className="text-white hover:text-blue-600">Terms</a>
          <a href="/privacy" className="text-white hover:text-blue-600">Privacy</a>
          <a href="/contact" className="text-white hover:text-blue-600">Contact</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
