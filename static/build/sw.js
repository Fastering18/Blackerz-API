importScripts('/cache-polyfill.js');


self.addEventListener('install', function(e) {
 e.waitUntil(
   caches.open('airhorner').then(function(cache) {
     return cache.addAll([
       '/',
       '/static/Images/Blackerz.jpg',
       '/static/Images/Blackerz.png',
       '/static/CSS/home.css',
       '/static/json/home.webmanifest'
     ]);
   })
 );
});
