import React from 'react';
import { Link } from 'react-router-dom';

const Unauthorized = () => (
  <div
    style={{
      padding: 40,
      maxWidth: 600,
      margin: '50px auto',
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif',
      color: '#b00020',
      border: '1px solid #f5c6cb',
      backgroundColor: '#f8d7da',
      borderRadius: 8,
    }}
  >
    <h2>Unauthorized Access</h2>
    <p>You do not have permission to view this page.</p>
    <Link to="/" style={{ textDecoration: 'none', color: '#721c24', fontWeight: 'bold' }}>
      Go to Home
    </Link>
  </div>
);

export default Unauthorized;
