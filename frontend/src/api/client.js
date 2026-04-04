import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL ||
  'https://hotel-reservation-system-backend-aeqb.onrender.com';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request when present
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;
