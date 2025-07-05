// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',  // ✅ Matches Flask's /api prefix
  withCredentials: true,                 // ✅ Enables auth/session cookies
});

export default api;
