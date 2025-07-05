// components/LiveDemo.jsx
export default function LiveDemo() {
  return (
    <section className="container mx-auto px-6 py-20 text-center">
      <h2 className="text-3xl font-bold mb-8">Live Demo Preview</h2>
      {/* Placeholder video */}
      <div className="aspect-w-16 aspect-h-9 max-w-4xl mx-auto shadow-lg rounded-lg overflow-hidden bg-gray-200 flex items-center justify-center text-gray-400">
        <span className="text-2xl">[Video or Annotated PDF Preview]</span>
      </div>
    </section>
  );
}
