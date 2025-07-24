import React, { useEffect, useState } from 'react';
import axios from '../services/api';

const TeacherDashboard = () => {
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    axios.get('/api/teacher/dashboard').then(res => {
      setSubmissions(res.data);
    });
  }, []);

  const handleDelete = async (submissionId) => {
    if (!window.confirm('Are you sure you want to delete this submission?')) return;

    try {
      const response = await fetch(`/api/v1/submissions/${submissionId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        alert('Submission deleted');
        setSubmissions(prev => prev.filter(s => s.id !== submissionId));
      } else {
        const err = await response.json();
        alert(`Error: ${err.error}`);
      }
    } catch (e) {
      alert('Network error while deleting submission');
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Teacher Dashboard</h2>
      <table className="w-full table-auto border-collapse">
        <thead>
          <tr>
            <th className="border p-2">Student</th>
            <th className="border p-2">Score</th>
            <th className="border p-2">View</th>
            <th className="border p-2">Actions</th> {/* ✅ New column */}
          </tr>
        </thead>
        <tbody>
          {submissions.map((s, i) => (
            <tr key={i}>
              <td className="border p-2">{s.student_name}</td>
              <td className="border p-2">{s.score}</td>
              <td className="border p-2">
                <a
                  href={s.marked_pdf_url}
                  target="_blank"
                  className="text-blue-600 underline"
                  rel="noreferrer"
                >
                  View
                </a>
              </td>
              <td className="border p-2">
                <button
                  onClick={() => handleDelete(s.id)}
                  className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                >
                  Delete
                </button>
              </td> {/* ✅ Delete button */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TeacherDashboard;
