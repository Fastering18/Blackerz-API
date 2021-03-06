window.setupganalytics = function(user) {
   if (!user.username || !user.id) return;
   gtag('set', 'user_properties', {
      Discord_Account:  user.username+" - "+user.id,
   });
}
