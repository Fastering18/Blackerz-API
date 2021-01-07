from flask_restful import Resource
from flask import jsonify, make_response
import time
from threading import Timer

from firebase import firebase
from util.database import data

class resource2(Resource):
  def get(self):
    botum = data("botlist")
    botlist = botum.data
    
    if botlist:
        return make_response(jsonify(botlist), 200)
    else: 
        return make_response("404 Bot tidak ditemukan.", 404)
