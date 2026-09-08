const CACHE = 'kmreg-v3';
const ASSETS = ['./', './index.html', './styles.css', './app.js', './manifest.webmanifest', './icons/icon.svg'];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
});

self.addEventListener('activate', event => {
  event.waitUntil(Promise.all([
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))),
    self.clients.claim()
  ]));
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  // Voor navigatie en appbestanden eerst het netwerk proberen, zodat GitHub-updates snel zichtbaar zijn.
  event.respondWith(
    fetch(event.request).then(resp => {
      const clone = resp.clone();
      caches.open(CACHE).then(c => c.put(event.request, clone));
      return resp;
    }).catch(() => caches.match(event.request).then(hit => hit || caches.match('./index.html')))
  );
});
