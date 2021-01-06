from flask_restful import Resource
from flask import jsonify, make_response
from threading import Timer

from firebase import firebase

botlist = {}
updated = false

def updated(bool):
    updated = bool

class data():
    def __init__(self, dataName):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist', None)
        self.data = result
        botlist = result
        updated = true
        Timer(60, updated, false)
        
class resouce(Resource):
  def get(self, id):
    if (updated == false):
        botum = data("botlist")
        botlist = botum.data
    print(botlist)
    
    if str(id) in botlist:
        return make_response(jsonify(botlist[str(id)]), 200)
    else: 
        return make_response("404 Bot tidak ditemukan., 200)
