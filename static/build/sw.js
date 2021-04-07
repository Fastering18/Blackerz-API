importScripts('https://arc.io/arc-sw-core.js');
self.addEventListener('fetch', (event) => {
  event.respondWith( 
    caches.match(event.request) 
      .then((response) => { 
        if (response) { 
          //entry found in cache 
          return response 
        } 
        return fetch(event.request) 
      } 
    ) 
  ) 
})
