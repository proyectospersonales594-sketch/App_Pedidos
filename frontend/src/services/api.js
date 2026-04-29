import axios from 'axios';

const api = axios.create({
  baseURL: 'http://192.168.1.2:8000', // IP de tu computador para acceso desde el celular
  timeout: 10000,
});

export default api;
