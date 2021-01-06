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

    return jsonify(bots[str(id)]), 200
