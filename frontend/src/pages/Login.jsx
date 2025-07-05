import React, { useState, useContext } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('teacher'); // default role
  const { user, login } = useContext(AuthContext);
  const navigate = useNavigate();

  if (user) {
    // Already logged in, redirect home
    return <Navigate to="/" replace />;
  }

  const handleSubmit = e => {
    e.preventDefault();
    login(username, role);
    navigate('/'); // redirect after login
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', padding: 20 }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Username: <br />
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
          />
        </label>
        <br />
        <label>
          Role: <br />
          <select value={role} onChange={e => setRole(e.target.value)}>
            <option value="teacher">Teacher</option>
            <option value="student">Student</option>
            <option value="admin">Admin</option>
          </select>
        </label>
        <br /><br />
        <button type="submit">Log In</button>
      </form>
    </div>
  );
};

export default Login;
