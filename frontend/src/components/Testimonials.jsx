// components/Testimonials.jsx
const testimonials = [
  { quote: 'Saved hours each week!', author: 'A Real Teacher' },
];

export default function Testimonials() {
  return (
    <section className="bg-blue-50 py-16 px-6 text-center">
      <h2 className="text-3xl font-bold mb-8">Testimonials</h2>
      <div className="max-w-2xl mx-auto text-gray-700 italic">
        {testimonials.map(({ quote, author }, idx) => (
          <blockquote key={idx} className="mb-6">
            “{quote}” <br />
            <span className="font-semibold text-blue-700">— {author}</span>
          </blockquote>
        ))}
      </div>
    </section>
  );
}
