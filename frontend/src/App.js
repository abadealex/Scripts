import React from 'react';
import './styles/App.css'; // ✅ Updated CSS path
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';

import UploadStudent from './components/UploadStudent';
import ResultViewer from './components/ResultViewer';
import TeacherDashboard from './components/TeacherDashboard';

function App() {
  return (
    <Router>
      <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <nav style={{ marginBottom: '20px' }}>
          <NavLink 
            to="/upload" 
            style={({ isActive }) => ({
              marginRight: '15px',
              textDecoration: 'none',
              color: isActive ? '#ff6347' : '#007bff',
            })}
          >
            Upload Student
          </NavLink>
          <NavLink 
            to="/results" 
            style={({ isActive }) => ({
              marginRight: '15px',
              textDecoration: 'none',
              color: isActive ? '#ff6347' : '#007bff',
            })}
          >
            View Results
          </NavLink>
          <NavLink 
            to="/teacher/dashboard" 
            style={({ isActive }) => ({
              textDecoration: 'none',
              color: isActive ? '#ff6347' : '#007bff',
            })}
          >
            Teacher Dashboard
          </NavLink>
        </nav>

        <Routes>
          <Route path="/upload" element={<UploadStudent />} />
          <Route path="/results" element={<ResultViewer />} />
          <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
          <Route path="/" element={<h2>Welcome! Use the navigation links above to get started.</h2>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
