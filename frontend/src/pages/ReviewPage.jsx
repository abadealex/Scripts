import React, { useEffect, useState } from "react";

// Mock API fetch function — replace with your real data fetching logic
async function fetchReviewData() {
  // Example data structure you might get from your backend API
  return {
    studentName: "John Doe",
    totalScore: 8.5,
    maxScore: 10,
    percentage: 85,
    questions: [
      {
        id: "q1",
        questionText: "What is a logic gate?",
        studentAnswer: "A device that performs logical operations",
        expectedAnswers: [
          "A device performing logical operations",
          "A basic building block in circuits",
        ],
        score: 3,
        maxMarks: 3,
        feedback: "Good answer!",
      },
      {
        id: "q2",
        questionText: "Explain AND gate behavior.",
        studentAnswer: "Output is 1 only if both inputs are 1.",
        expectedAnswers: ["Output is 1 only if both inputs are 1."],
        score: 2.5,
        maxMarks: 3,
        feedback: "Partial credit, could elaborate more.",
      },
      {
        id: "q3",
        questionText: "What is an OR gate?",
        studentAnswer: "Output is 1 if any input is 1.",
        expectedAnswers: ["Output is 1 if at least one input is 1."],
        score: 3,
        maxMarks: 4,
        feedback: "Good, but missed edge cases.",
      },
    ],
  };
}

const ReviewPage = () => {
  const [loading, setLoading] = useState(true);
  const [reviewData, setReviewData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch review data on mount
    fetchReviewData()
      .then((data) => {
        setReviewData(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load review data.");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading review data...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!reviewData) return <p>No review data available.</p>;

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "0 auto",
        padding: 20,
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Review for {reviewData.studentName}</h1>
      <h2>
        Total Score: {reviewData.totalScore} / {reviewData.maxScore} (
        {reviewData.percentage}%)
      </h2>
      <hr />

      {reviewData.questions.map((q, idx) => (
        <div
          key={q.id}
          style={{
            border: "1px solid #ccc",
            padding: 15,
            marginBottom: 20,
            borderRadius: 5,
            backgroundColor:
              q.score === q.maxMarks
                ? "#d4edda"
                : q.score > 0
                ? "#fff3cd"
                : "#f8d7da",
          }}
        >
          <h3>
            Question {idx + 1}: {q.questionText}
          </h3>
          <p>
            <strong>Your Answer:</strong>{" "}
            {q.studentAnswer || <em>No answer provided</em>}
          </p>
          <p>
            <strong>Expected Answer(s):</strong> {q.expectedAnswers.join("; ")}
          </p>
          <p>
            <strong>Score:</strong> {q.score} / {q.maxMarks}
          </p>
          <p>
            <strong>Feedback:</strong> {q.feedback || "No feedback available."}
          </p>
        </div>
      ))}
    </div>
  );
};

export default ReviewPage;
