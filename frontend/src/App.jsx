// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import ReviewPage from './pages/ReviewPage';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';
import RoleBasedRoute from './components/RoleBasedRoute';
import BulkUploadForm from './components/BulkUploadForm';

const App = () => (
  <AuthProvider>
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
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
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
      </Routes>
    </Router>
  </AuthProvider>
);

export default App;
