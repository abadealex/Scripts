// src/components/Header.jsx
import React from 'react';

const Header = () => {
  return (
    <nav className="bg-white shadow-md py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center px-4">
        {/* Logo and brand name */}
        <a href="/" className="font-semibold text-2xl text-blue-600">SmartScripts</a>

        {/* Navigation links */}
        <ul className="flex space-x-6">
          <li><a href="#features" className="text-gray-800 hover:text-blue-600">Features</a></li>
          <li><a href="#pricing" className="text-gray-800 hover:text-blue-600">Pricing</a></li>
          <li><a href="#about" className="text-gray-800 hover:text-blue-600">About</a></li>
          
          {/* Authentication Links */}
          <li><a href="/login" className="text-blue-600 hover:text-blue-800">Login</a></li>
          <li><a href="/register" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Sign Up</a></li>
        </ul>
      </div>
    </nav>
  );
};

export default Header;
