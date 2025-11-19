/**
 * Sanctuary VR - Service Worker for PWA
 * Enables offline capabilities and caching
 */

const CACHE_NAME = 'sanctuary-v0.1.0';
const RUNTIME_CACHE = 'sanctuary-runtime';

// Assets to cache on install
const PRECACHE_URLS = [
    '/',
    '/index.html',
    '/css/main.css',
    '/js/config.js',
    '/js/api-client.js',
    '/js/medusa-avatar.js',
    '/js/biome-controller.js',
    '/js/creation-manager.js',
    '/js/main.js',
    '/manifest.json',
    '/icons/icon-192.png',
    '/icons/icon-512.png'
];

// Install event - cache essential assets
self.addEventListener('install', event => {
    console.log('[ServiceWorker] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[ServiceWorker] Caching app shell');
                return cache.addAll(PRECACHE_URLS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[ServiceWorker] Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
                        console.log('[ServiceWorker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    // API requests - network first, cache fallback
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            caches.open(RUNTIME_CACHE).then(cache => {
                return fetch(event.request)
                    .then(response => {
                        cache.put(event.request, response.clone());
                        return response;
                    })
                    .catch(() => cache.match(event.request))
            })
        );
        return;
    }

    // Static assets - cache first, network fallback
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse;
            }

            return caches.open(RUNTIME_CACHE).then(cache => {
                return fetch(event.request).then(response => {
                    cache.put(event.request, response.clone());
                    return response;
                });
            });
        }).catch(() => {
            // Offline fallback page (optional)
            if (event.request.destination === 'document') {
                return caches.match('/offline.html');
            }
        })
    );
});

// Listen for skip waiting message
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
