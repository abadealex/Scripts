// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Pages
import HomePage from './pages/HomePage';
import ReviewPage from './pages/ReviewPage';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';

// Components
import RoleBasedRoute from './components/RoleBasedRoute';
import BulkUploadForm from './components/BulkUploadForm';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* ✅ Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* 🔐 Protected Teacher Routes */}
          <Route
            path="/teacher/review"
            element={
              <RoleBasedRoute allowedRoles={['teacher']}>
                <ReviewPage />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/teacher/upload"
            element={
              <RoleBasedRoute allowedRoles={['teacher']}>
                <BulkUploadForm />
              </RoleBasedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
