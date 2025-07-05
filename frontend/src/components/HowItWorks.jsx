// components/HowItWorks.jsx
const steps = [
  { number: 1, title: 'Upload', desc: 'Submit student papers or exams.' },
  { number: 2, title: 'AI Grades', desc: 'Let the AI analyze and grade quickly.' },
  { number: 3, title: 'Export Feedback', desc: 'Download annotated results for review.' },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-gray-100 py-20 px-6">
      <div className="container mx-auto max-w-4xl">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="flex flex-col md:flex-row justify-between gap-8">
          {steps.map(({ number, title, desc }) => (
            <div key={number} className="bg-white p-6 rounded-lg shadow-md flex-1 text-center">
              <div className="text-blue-600 text-4xl font-bold mb-4">{number}</div>
              <h3 className="text-xl font-semibold mb-2">{title}</h3>
              <p className="text-gray-700">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
