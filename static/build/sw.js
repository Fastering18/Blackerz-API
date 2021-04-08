importScripts('https://arc.io/arc-sw-core.js');

/*self.addEventListener('fetch', function(event){
   event.respondWith(async function () {
      var cache = await caches.open('cache');
      var cachedResponsePromise = await cache.match(event.request);
      var networkResponsePromise = fetch(event.request);
      event.waitUntil(async function () {
         var networkResponse = await networkResponsePromise;
         await cache.put(event.request, networkResponse.clone());
      }());
      return cachedResponsePromise || networkResponsePromise;
    }());
});

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open('cache').then(function(cache) {
      return cache.addAll([
        "./",
        "./servers",
        "./static/CSS/home.css",
        "./static/js/ga.js"
       ]);
    })
   );
});*/
