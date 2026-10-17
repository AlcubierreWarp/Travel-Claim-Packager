// CAF Digital Travel Itinerary: offline helper.
// Keeps a copy of this app's own files so the installed app opens without a connection.
// It only ever handles requests to this same site, and it never sees or sends claim data,
// which stays in the page's own device storage.
// Production and beta live on the same site, so each keeps its own cache, named after its folder.
const SCOPE = new URL(self.registration.scope).pathname;
const PREFIX = 'caf-dti-' + SCOPE + '-';
const CACHE = PREFIX + '569dcb7a37';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-192.png', './icon-maskable-512.png', './apple-touch-icon.png', './favicon.ico', './favicon-32x32.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith(PREFIX) && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  // Network first, so updates arrive as soon as you are online; fall back to the saved copy offline.
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match('./index.html')))
  );
});
