// CAF Digital Travel Itinerary: offline helper.
// Keeps a copy of this app's own files so the installed app opens without a connection.
// It only ever handles requests to this same site, and it never sees or sends claim data,
// which stays in the page's own device storage.
// Production and beta live on the same site, so each keeps its own cache, named after its folder.
const SCOPE = new URL(self.registration.scope).pathname;
const PREFIX = 'caf-dti-' + SCOPE + '-';
const CACHE = PREFIX + 'e0482930ee';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-192.png', './icon-maskable-512.png', './apple-touch-icon.png', './favicon.ico', './favicon-32x32.png'];
// The published offline file, kept so Download offline copy works offline too. Optional: the app still installs without it.
const OFFLINE_FILE = './CAF_Digital_Travel_Itinerary.html';
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES).then(() => c.add(OFFLINE_FILE).catch(() => {}))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith(PREFIX) && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  // Network first, so updates arrive as soon as you are online; fall back to the saved copy offline.
  // The page itself is always checked with the server (no-cache), so a stale browser copy is never shown.
  // Only the app's own page counts as the app: another page opened under this address (the offline
  // file, say) is fetched and kept under its own name, so it can never replace the saved app.
  const scope = new URL(self.registration.scope).pathname;
  const nav = e.request.mode === 'navigate' && (url.pathname === scope || url.pathname === scope + 'index.html');
  const other = e.request.mode === 'navigate' && !nav;
  const page = new URL('./index.html', self.registration.scope).href;
  const key = nav ? page : other ? url.origin + url.pathname : e.request;
  e.respondWith(
    (nav || other ? fetch(url.origin + url.pathname, { cache: 'no-cache', credentials: 'same-origin' }) : fetch(e.request)).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(key, copy)); }
      return res;
    }).catch(() => caches.match(key, { ignoreSearch: true }).then(r => r || (other ? Response.error() : caches.match(page))))
  );
});
