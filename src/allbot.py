from flask_restful import Resource
from flask import jsonify, make_response, request
from src.util.database import mongoDB
from bson.json_util import dumps
          
class resource2(Resource):
  def get(self):
    botlist = mongoDB().getAllBots()
    
    if isinstance(botlist, str):
      return make_response(botlist, 500)
    elif botlist: 
      return make_response(botlist, 200)
    else:
      return make_response("404 Bot tidak ditemukan.", 404)
