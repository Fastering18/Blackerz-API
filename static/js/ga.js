window.setupganalytics = function(user) {
   gtag('set', 'user_properties', {
      Discord_Account:  user.username+" - "+user.id,
   });
}
