from flask_restful import Resource
from flask import jsonify, make_response
import time
from threading import Timer

from firebase import firebase
from util.database import data

timeStamp = 0
botlistGlobal = {}
        
class resouce(Resource):
  def get(self, id):
    botum = data("botlist")
    botlist = botum.data
    print(botlist)
    
    if str(id) in botlist:
        return make_response(jsonify(botlist[str(id)]), 200)
    else: 
        return make_response("404 Bot tidak ditemukan.", 404)
