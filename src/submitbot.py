from flask_restful import Resource
from flask import jsonify, make_response, request
import time
from threading import Timer

from firebase import firebase

timeStamp = 0
botlistGlobal = {}
    
class data():
    def __init__(self, dataName):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist', None)
        self.data = result
        botlistGlobal = result
        timeStamp = time.time()
        
class resouce(Resource):
  def put(self, id):
    data = request.form['data']

    return make_response("sedang maintenance", 400)
