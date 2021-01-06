from flask_restful import Resource
from flask import jsonify

from firebase import firebase


class data():
    def __init__(self, dataName):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist', None)
        self.data = result
        
class resouce(Resource):
  def get(self, id):
    botum = data("botlist")
    bots = botum.data
    print(bots)

    if id in bots:
        return jsonify(bots[id])
    else:
        return "<h1>404 Bot tidak ditemukan untuk id: {}".format(id), 404
