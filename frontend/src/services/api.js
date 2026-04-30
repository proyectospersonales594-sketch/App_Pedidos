import axios from 'axios';

const api = axios.create({
  // Si existe VITE_API_URL en el entorno (Vercel), la usa; si no, usa la de Render directamente
  baseURL: import.meta.env.VITE_API_URL || 'https://app-pedidos-fwze.onrender.com',
  timeout: 15000,
});

export default api;
