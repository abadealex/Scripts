// components/HeroSection.jsx
export default function HeroSection() {
  return (
    <section className="bg-blue-50 py-20 text-center px-6">
      <h1 className="text-4xl md:text-5xl font-extrabold text-blue-700 mb-4">
        Automated Grading Made Simple
      </h1>
      <p className="text-lg md:text-xl text-gray-700 mb-8">
        Grade papers 10x faster using AI
      </p>
      <div className="space-x-4">
        <a href="/signup" className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
          Get Started
        </a>
        <a href="#how-it-works" className="text-blue-600 font-semibold hover:underline">
          See How It Works
        </a>
      </div>
    </section>
  );
}
