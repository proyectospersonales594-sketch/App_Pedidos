import axios from 'axios';

const api = axios.create({
  // Detecta automáticamente si usar el servidor local o el de producción
  baseURL: import.meta.env.VITE_API_URL || 
           (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? 'http://localhost:8000' 
            : 'https://app-pedidos-fwze.onrender.com'),
  timeout: 15000,
});

export default api;
