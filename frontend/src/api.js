import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api', // update this if your Flask backend uses a different base URL
  withCredentials: true, // if using cookies or auth
});

export default api;
