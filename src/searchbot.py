from flask_restful import Resource
from flask import jsonify, make_response
import time
from threading import Timer

from firebase import firebase

class data():
    def __init__(self, dataName):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist', None)
        self.data = result
        botlistGlobal = result
        timeStamp = time.time()

timeStamp = 0
botlistGlobal = {}
error1 = {'error': "Bot not found", 'status': "Not success"}
        
class resouce(Resource):
  def get(self, id):
    botum = data("botlist")
    botlist = botum.data
    
    if str(id) in botlist:
        return make_response(jsonify(botlist[str(id)]), 200)
    else: 
        return make_response(jsonify(error1), 404)
