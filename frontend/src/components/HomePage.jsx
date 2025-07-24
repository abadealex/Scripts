// src/pages/HomePage.jsx
import React from 'react';
import Header from '../components/Header';
import HeroSection from '../components/HeroSection';
import Features from '../components/Features';
import HowItWorks from '../components/HowItWorks';
import Footer from '../components/Footer';

const HomePage = () => {
  return (
    <div>
      <Header />
      <HeroSection />
      <Features />
      <HowItWorks />
      <Footer />
    </div>
  );
};

export default HomePage;
