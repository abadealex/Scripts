import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MyResults = () => {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSubmissions = async () => {
      try {
        const res = await axios.get('/api/v1/submissions/my_submissions', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setSubmissions(res.data);
      } catch (err) {
        console.error('Failed to fetch submissions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSubmissions();
  }, []);

  if (loading) return <p>Loading your results...</p>;
  if (!submissions.length) return <p>No submissions found.</p>;

  return (
    <div className="my-results container">
      <h1>My Submissions & Feedback</h1>
      <ul>
        {submissions.map((submission, idx) => (
          <li key={idx} className="result-item">
            <h3>Test ID: {submission.test_id || 'N/A'}</h3>
            <p><strong>Score:</strong> {submission.score}</p>
            {submission.feedback && (
              <p><strong>Feedback:</strong> {submission.feedback}</p>
            )}
            {submission.file_url && (
              <p>
                <a href={submission.file_url} target="_blank" rel="noopener noreferrer">
                  View Graded File
                </a>
              </p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MyResults;
