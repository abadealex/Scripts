import React, { useEffect, useState } from 'react';
import api from '../services/api';

const ResultViewer = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    api.get('/api/student/results').then(res => {
      setResults(res.data);
    });
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Your Results</h2>
      <ul className="space-y-2">
        {results.map((r, i) => (
          <li key={i} className="border p-2 rounded shadow">
            <p><strong>Score:</strong> {r.score}</p>
            <a
              href={r.marked_pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline"
            >
              View Marked PDF
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ResultViewer;
