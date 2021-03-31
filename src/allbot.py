from flask_restful import Resource
from flask import jsonify, make_response, request
import time, requests, os
from threading import Timer
from src.util.database import *

from firebase import firebase

FirebaseBaseURL = os.environ.get('FIREBASE_BASE_URL', 'https://blackerz-default-rtdb.firebaseio.com/')
firebaseDB = firebase.FirebaseApplication(FirebaseBaseURL, None)
botCaches = {}

def deleteCache(tipe="botsverified"):
  del botCaches[tipe]
  return True

def putCache(tipe, isi):
    botCaches[tipe] = isi
    Timer(300.0, deleteCache, [tipe]).start()
    return True

class data():
    def __init__(self, dataName):
        if dataName == "verifiedbots":
            try:
                result = requests.get('https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy=%22verified%22&equalTo=true').json() # FirebaseBaseURL + 'Infrastructure/botlist?orderBy="verified"&equalTo=true'
                self.data = result
                putCache("botsverified", self.data)
            except Exception as kesalahan:
                self.data = "Internal error, this is not your error, please report this issues to github."
                print(kesalahan)
          

class resource2(Resource):
  def get(self):
    #if "botsverified" in botCaches:
      #return make_response(jsonify(botCaches["botsverified"]), 200)
    botlist = dataManager().getAllBots() #botum = data("verifiedbots") 
    #botlist = botum.data
    
    if isinstance(botlist, str):
      return make_response(botlist, 500)
    elif botlist: 
      return make_response(jsonify(botlist), 200)
    else:
      return make_response("404 Bot tidak ditemukan.", 404)
