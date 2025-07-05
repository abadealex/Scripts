// App.jsx
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import LiveDemo from './components/LiveDemo';
import Testimonials from './components/Testimonials';
import CtaFooter from './components/CtaFooter';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <HeroSection />
        <Features />
        <HowItWorks />
        <LiveDemo />
        <Testimonials />
        <CtaFooter />
      </main>
      <Footer />
    </div>
  );
}

export default App;
