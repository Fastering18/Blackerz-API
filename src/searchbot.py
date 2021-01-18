from flask_restful import Resource
from flask import jsonify, make_response
import time
import requests
from threading import Timer

from firebase import firebase

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"

class data():
    def __init__(self, dataName, id):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist', None)
        
        url = "https://discord.com/api/v8/users/" + id
        r = requests.get(url = URL, headers={'Authorization': 'Bot ' + botToken}) 
        response = r.json() 
        print(response)
        
        self.data = result
        botlistGlobal = result
        timeStamp = time.time()

timeStamp = 0
botlistGlobal = {}
error1 = {'error': "Bot not found", 'status': "Not success"}
        
class resouce(Resource):
  def get(self, id):
    botum = data("botlist", id)
    botlist = botum.data
    
    if str(id) in botlist:
        return make_response(jsonify(botlist[str(id)]), 200)
    else: 
        return make_response(jsonify(error1), 404)
