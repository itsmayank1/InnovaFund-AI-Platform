import axios from "axios";

// Backend base URL. Set VITE_API_URL in the deployment environment
// (e.g. https://innovafund-api.onrender.com). Falls back to the local backend.
const API_ROOT =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: `${API_ROOT}/api`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;