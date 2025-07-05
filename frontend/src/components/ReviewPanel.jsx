import api from '../services/api';
import React, { useEffect, useState } from 'react';
import axios from '../services/api';

const ReviewPanel = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const res = await api.('/api/student/reviews');
        setReviews(res.data);
      } catch (err) {
        setError('Failed to load reviews.');
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, []);

  if (loading) return <p>Loading reviews...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Student Feedback & Reviews</h2>
      {reviews.length === 0 ? (
        <p>No reviews found.</p>
      ) : (
        <ul className="space-y-4">
          {reviews.map((review, idx) => (
            <li key={idx} className="border rounded p-4 shadow">
              <p><strong>From:</strong> {review.student_name || 'Anonymous'}</p>
              <p><strong>Comment:</strong> {review.comment}</p>
              <p><strong>Date:</strong> {new Date(review.date).toLocaleDateString()}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ReviewPanel;


