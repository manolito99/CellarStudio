const CACHE_NAME = 'cellarstudio-v1'
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
]

// Install: cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  )
  self.skipWaiting()
})

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  )
  self.clients.claim()
})

// Fetch: network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event

  // Skip non-http(s) and API calls
  if (!request.url.startsWith('http')) return
  if (request.url.includes('/api/')) return

  event.respondWith(
    fetch(request)
      .then((response) => {
        // Cache successful GET responses
        if (request.method === 'GET' && response.status === 200) {
          const clone = response.clone()
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
        }
        return response
      })
      .catch(() => caches.match(request).then((cached) => cached || caches.match('/')))
  )
})

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {}
  const title = data.title || 'Cellar Barber Studio'
  const options = {
    body: data.body || 'Tienes un recordatorio',
    icon: data.icon || '/icons/CellarStudio_Logo.png',
    badge: data.badge || '/icons/CellarStudio_Logo.png',
    data: data.data || {},
    vibrate: [200, 100, 200],
  }
  event.waitUntil(self.registration.showNotification(title, options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url || '/'
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(url) && 'focus' in client) return client.focus()
      }
      return self.clients.openWindow(url)
    })
  )
})
