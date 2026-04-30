// Service Worker básico para permitir la instalación como PWA
self.addEventListener('install', (event) => {
  console.log('Service Worker instalado');
});

self.addEventListener('fetch', (event) => {
  // Solo pasamos las peticiones, necesario para cumplir requisitos PWA
  event.respondWith(fetch(event.request));
});
