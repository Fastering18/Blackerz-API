from flask_restful import Resource
from flask import jsonify, make_response, render_template
import time
import requests
from threading import Timer

from firebase import firebase

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
            
class data():
    def __init__(self, dataName, id):
        result = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
        if result != None:       
            url = "https://discord.com/api/v8/users/" + str(id)
            r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
            response = r.json() 

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
        else:
            self.data = None
            
error1 = {'error': "Bot not found", 'status': "Not success"}
        
class botPage(Resource):
  def get(self, id):
    botum = data("getbot", id)
    bot = botum.data
    
    if bot != None:
        botName = bot["name"]
        short_description = bot["ShortDescription"]
        return render_template('botPage.html', botName = botName, short_description = short_description)
    else:
        botName = "Bot not found"
        short_description = ""
        return render_template('botPage.html', botName = botName, short_description = short_description)
