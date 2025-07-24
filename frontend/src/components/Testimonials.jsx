// src/components/Testimonials.jsx

import React from 'react';

const Testimonials = () => {
  return (
    <section id="testimonials" className="py-16 bg-white">
      <div className="container mx-auto text-center">
        <h2 className="text-3xl font-semibold text-gray-900">Trusted by Teachers Worldwide</h2>
        <p className="mt-4 text-xl text-gray-600">Used by over 1,000 educators in 10+ countries</p>
        <div className="d-flex justify-content-center gap-4 flex-wrap mt-8">
          <img src="https://via.placeholder.com/100x40?text=School+1" alt="School Logo" />
          <img src="https://via.placeholder.com/100x40?text=School+2" alt="School Logo" />
          <img src="https://via.placeholder.com/100x40?text=College+3" alt="College Logo" />
          <img src="https://via.placeholder.com/100x40?text=District+4" alt="District Logo" />
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
