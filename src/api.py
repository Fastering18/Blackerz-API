from flask_restful import Resource
from flask import jsonify

from database import data

bots = data("botlist")

class resouce(Resource):
  def get(self, id):
    if id in bots:
        return jsonify(bots[id])
    else:
        return "<h1>404 Bot tidak ditemukan untuk id: {}".format(id), 404
