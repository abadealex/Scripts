import React, { useEffect, useState } from 'react';
import axios from '../api';

const TeacherDashboard = () => {
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    axios.get('/teacher/dashboard').then(res => {
      setSubmissions(res.data);
    });
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Teacher Dashboard</h2>
      <table className="w-full table-auto border-collapse">
        <thead>
          <tr>
            <th className="border p-2">Student</th>
            <th className="border p-2">Score</th>
            <th className="border p-2">View</th>
          </tr>
        </thead>
        <tbody>
          {submissions.map((s, i) => (
            <tr key={i}>
              <td className="border p-2">{s.student_name}</td>
              <td className="border p-2">{s.score}</td>
              <td className="border p-2">
                <a href={s.marked_pdf_url} target="_blank" className="text-blue-600 underline" rel="noreferrer">View</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TeacherDashboard;
