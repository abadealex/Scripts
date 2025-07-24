import React, { useEffect, useState } from 'react';
import BiasAuditDashboard from '../components/BiasAuditDashboard';

const Audit = () => {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch audit and fairness data from backend API
    fetch('/api/v1/audit/report')
      .then(res => res.json())
      .then(data => {
        setAuditData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch audit data:', err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="audit-page container">
      <h1>Teacher Audit & Fairness Overview</h1>
      {loading && <p>Loading audit data...</p>}
      {!loading && auditData && <BiasAuditDashboard data={auditData} />}
      {!loading && !auditData && <p>No audit data available.</p>}
    </div>
  );
};

export default Audit;
