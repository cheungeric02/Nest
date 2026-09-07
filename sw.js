/* Nest service worker — offline shell cache */
const CACHE = 'nest-v1';
const ASSETS = ['./', './index.html', './manifest.json', './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(
    ASSETS.map(u => c.add(new Request(u, {cache:'reload'})).catch(()=>{}))
  )));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(()=>self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Never cache Firebase / Google auth traffic
  if (/gstatic|googleapis|firebaseio|google\.com/.test(url.hostname)) return;
  // Network-first for the HTML shell so updates land; cache fallback offline
  if (req.mode === 'navigate' || url.pathname.endsWith('index.html')) {
    e.respondWith(fetch(req).then(r => {
      const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return r;
    }).catch(() => caches.match(req).then(m => m || caches.match('./index.html'))));
    return;
  }
  // Cache-first for other same-origin assets
  if (url.origin === location.origin) {
    e.respondWith(caches.match(req).then(m => m || fetch(req).then(r => {
      const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return r;
    })));
  }
});
