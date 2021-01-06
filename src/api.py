from flask_restful import Resource
from flask import jsonify, make_response
from threading import Timer

from firebase import firebase

def updated(status):
    updated = bool(status)

class data():
    def __init__(self, dataName):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist', None)
        self.data = result
        global botlist = result
        global updated = bool(0)
        Timer(60, updated, 1)
        
class resouce(Resource):
  def get(self, id):
    if (updated == False):
        botum = data("botlist")
        global botlist = botum.data
    print(botlist)
    
    if str(id) in botlist:
        return make_response(jsonify(botlist[str(id)]), 200)
    else: 
        return make_response("404 Bot tidak ditemukan.", 404)
