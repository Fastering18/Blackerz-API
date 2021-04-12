from flask_restful import Resource
from flask import jsonify, make_response
import time, requests
from threading import Timer
from src.util.database import mongoDB
from bson.json_util import dumps

from firebase import firebase

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

class data():
    def __init__(self, dataName):
        result = firebaseDB.get('/Infrastructure/serverlist/', None)
        if result != None:       
            self.data = result
            self.timeStamp = time.time()
        else:
            self.data = None

error1 = {'error': "Server not found", 'status': "Not success"}
        
class findAllServer(Resource):
  def get(self):
    servers = mongoDB().getAllServers() #data("getserver")
    
    if servers != None:
        return make_response(dumps(servers), 200, {'Content-Type': 'application/json'})
    else: 
        return make_response(jsonify(error1), 404, {'Content-Type': 'application/json'})
