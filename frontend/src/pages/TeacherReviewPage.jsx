import React from 'react';
import { Link } from 'react-router-dom';

const TeacherReviewPage = () => {
  return (
    <div className="container my-5">
      <h1>Teacher Review Page</h1>
      <p>Welcome to the Teacher Review Page. Here you can manage reviews and feedback.</p>

      <div className="mt-4 d-flex gap-2">
        <Link to="/review" className="btn btn-success">
          Go to Review Page
        </Link>
        <Link to="/teacher/dashboard" className="btn btn-primary">
          ← Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default TeacherReviewPage;
