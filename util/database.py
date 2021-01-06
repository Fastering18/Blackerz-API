from firebase import firebase

firebase = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
result = firebase.get('/Infrastructure/botlist', None)
print result
