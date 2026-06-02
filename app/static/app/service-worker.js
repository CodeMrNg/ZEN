const CACHE_NAME = "zen-trading-pwa-20260602-1";
const APP_SHELL = [
    "/static/app/offline.html",
    "/static/app/dashboard.css",
    "/static/app/ui.js",
    "/static/app/pwa.js",
    "/static/app/logo.png",
    "/static/app/favicon.png",
    "/static/app/pwa-icon-192.png",
    "/static/app/pwa-icon-512.png",
    "/static/vendor/chart.umd.min.js",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(APP_SHELL))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => Promise.all(
                cacheNames
                    .filter((cacheName) => cacheName !== CACHE_NAME)
                    .map((cacheName) => caches.delete(cacheName))
            ))
            .then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", (event) => {
    const request = event.request;
    const url = new URL(request.url);

    if (request.method !== "GET" || url.origin !== self.location.origin) {
        return;
    }

    if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/admin/")) {
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request)
                .catch(() => caches.match("/static/app/offline.html"))
        );
        return;
    }

    event.respondWith(
        caches.match(request).then((cached) => {
            if (cached) {
                return cached;
            }

            return fetch(request).then((response) => {
                if (response.ok && (
                    url.pathname.startsWith("/static/") ||
                    url.pathname === "/manifest.webmanifest" ||
                    url.pathname === "/service-worker.js"
                )) {
                    const copy = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
                }
                return response;
            });
        })
    );
});
