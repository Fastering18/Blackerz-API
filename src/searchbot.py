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
        result = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
        if result == None : return;
        
        url = "https://discord.com/api/v8/users/" + str(id)
        r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
        response = r.json() 
        print(response)
        if result["name"] != response["username"]:
            result["name"] = response["username"]
            firebaseDB.put('/Infrastructure/botlist/' + str(id), "name", response["username"])
        if "avatar" in result and "avatar" in response:
            if result["avatar"] != response["avatar"]:
                 result["avatar"] = response["avatar"]
                 firebaseDB.put('/Infrastructure/botlist/' + str(id), "avatar", response["avatar"])       
        elif "avatar" in response and not "avatar" in result:
            result["avatar"] = response["avatar"]
            firebaseDB.put('/Infrastructure/botlist/' + str(id), "avatar", response["avatar"])
        self.data = result
        self.timeStamp = time.time()

timeStamp = 0
error1 = {'error': "Bot not found", 'status': "Not success"}
        
class resouce(Resource):
  def get(self, id):
    botum = data("getbot", id)
    if not "data" in botum : return; 
    bot = botum.data
    
    if bot != None:
        return make_response(jsonify(bot), 200)
    else: 
        return make_response(jsonify(error1), 404)
