import React, { useEffect, useState } from "react";

const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Example fetch to your updated API endpoint
    fetch(/analytics")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Error fetching analytics: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        setAnalyticsData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading analytics data...</p>;
  if (error) return <p>Error: {error}</p>;

  // Example rendering assuming analyticsData has these fields:
  // totalStudents, averageScore, submissionsByDate (array of {date, count})

  return (
    <div className="analytics-dashboard">
      <h2>Analytics Dashboard</h2>
      <div>
        <strong>Total Students:</strong> {analyticsData.totalStudents}
      </div>
      <div>
        <strong>Average Score:</strong> {analyticsData.averageScore.toFixed(2)}
      </div>

      <h3>Submissions Over Time</h3>
      <ul>
        {analyticsData.submissionsByDate.map(({ date, count }) => (
          <li key={date}>
            {date}: {count} submissions
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AnalyticsDashboard;

