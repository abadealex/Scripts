import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import FeedbackOverlay from '../components/FeedbackOverlay';
import api from '../services/api';

const StudentResultsPage = () => {
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  // Fetch submission data on mount
  useEffect(() => {
    const fetchSubmission = async () => {
      try {
        const { data } = await api.get('/student/submission/123'); // Replace with dynamic ID if needed
        setSubmission(data);
      } catch (err) {
        console.error('Failed to fetch submission:', err);
        setError('Failed to load submission data.');
      } finally {
        setLoading(false);
      }
    };

    fetchSubmission();
  }, []);

  const formatDateTime = (ts) => {
    if (!ts) return 'N/A';
    const date = new Date(ts);
    return date.toLocaleString();
  };

  const handleReviewClick = () => {
    // Navigate to ReviewPage (adjust route as needed)
    navigate('/review');
  };

  if (loading) return <p className="text-center mt-5">Loading...</p>;
  if (error) return <p className="text-danger text-center mt-5">{error}</p>;
  if (!submission) return <p className="text-center mt-5">No submission found.</p>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">Submission Result</h1>

      <div className="mb-3">
        <p><strong>ID:</strong> {submission.id}</p>
        <p><strong>Subject:</strong> {submission.subject || 'N/A'}</p>
        <p><strong>Grade:</strong> {submission.grade || 'Pending'}</p>
        <p><strong>AI Confidence:</strong> {submission.ai_confidence || 'N/A'}</p>
        <p><strong>Submitted At:</strong> {formatDateTime(submission.timestamp)}</p>
      </div>

      <h2 className="mt-4">🖼️ Graded Image + Feedback</h2>

      {submission.graded_image ? (
        <FeedbackOverlay
          imageUrl={`/static/${submission.graded_image}`}
          feedbackItems={submission.feedbackOverlays || []}
        />
      ) : (
        <p className="text-muted">No graded image available.</p>
      )}

      <div className="mt-4 d-flex gap-2">
        <button className="btn btn-success" onClick={handleReviewClick}>
          Go to Review Page
        </button>
        <Link to="/student/dashboard" className="btn btn-primary">
          ← Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default StudentResultsPage;
