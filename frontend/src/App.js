import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

import UploadStudent from './components/UploadStudent';
import ResultViewer from './components/ResultViewer';
import TeacherDashboard from './components/TeacherDashboard';

function App() {
  return (
    <Router>
      <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <nav style={{ marginBottom: '20px' }}>
          <Link to="/student/upload" style={{ marginRight: '15px', textDecoration: 'none', color: '#007bff' }}>Upload Student</Link>
          <Link to="/student/results" style={{ marginRight: '15px', textDecoration: 'none', color: '#007bff' }}>View Results</Link>
          <Link to="/teacher/dashboard" style={{ textDecoration: 'none', color: '#007bff' }}>Teacher Dashboard</Link>
        </nav>

        <Routes>
          <Route path="/student/upload" element={<UploadStudent />} />
          <Route path="/student/results" element={<ResultViewer />} />
          <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
          <Route path="/" element={<h2>Welcome! Use the navigation links above to get started.</h2>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
