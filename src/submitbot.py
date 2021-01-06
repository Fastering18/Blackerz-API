from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request
import time
from threading import Timer

from firebase import firebase

parser = reqparse.RequestParser()
parser.add_argument('data')

timeStamp = 0
botlistGlobal = {}

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)   
    
class postBot():
    def __init__(self, dataREQ):
         data =  { 'name': dataREQ.name,
          'owner': {
             'id': dataREQ.author.id,
             'name': dataREQ.author.name
          },
          'tag': dataREQ.tag,
          'upvotes': 0
          }
          result = firebaseDB.post('/Infrastructure/botlist/' + dataREQ.id, data)
        
class resource3(Resource):
  def put(self, id):
    data = parser.parse_args()['data']
    result = postBot(data)
    
    return make_response("sedang maintenance", 400)
