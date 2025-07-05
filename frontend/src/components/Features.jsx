// components/Features.jsx
const features = [
  { icon: '🧠', title: 'AI Scoring', desc: 'Automatically score student answers with AI-powered precision.' },
  { icon: '📷', title: 'OCR Extraction', desc: 'Extract text from images and handwritten notes seamlessly.' },
  { icon: '✍️', title: 'Manual Review', desc: 'Easily review and adjust scores manually when needed.' },
];

export default function Features() {
  return (
    <section className="container mx-auto px-6 py-16 grid md:grid-cols-3 gap-10 text-center">
      {features.map(({ icon, title, desc }) => (
        <div key={title} className="bg-white rounded-lg p-8 shadow-md">
          <div className="text-6xl mb-4">{icon}</div>
          <h3 className="text-xl font-semibold mb-2">{title}</h3>
          <p className="text-gray-600">{desc}</p>
        </div>
      ))}
    </section>
  );
}
