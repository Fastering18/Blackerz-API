from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request, abort
import time
import json
from threading import Timer

from firebase import firebase

parser = reqparse.RequestParser()
parser.add_argument('data')

timeStamp = 0
botlistGlobal = {}

firebaseDB = firebase.FirebaseApplication(
    'https://blackerz-default-rtdb.firebaseio.com/', None)


class postBot():
    def __init__(self, dataREQ):
        dataFinal = {'name': dataREQ['name'],
                'owner': {
                    'id': dataREQ['owner']['id'],
                    'name': dataREQ['owner']['name']
                },
                'tag': dataREQ['tag'],
                'upvotes': 0
                }
        self.result = firebaseDB.post('/Infrastructure/botlist/' + dataREQ['id'], data=dataFinal, params={'print': 'pretty'})


class resource3(Resource):
    def post(self, id):
        jsonData = request.get_json()
        print(jsonData)
        
        if not jsonData or not 'name' in jsonData or not 'owner' in jsonData:
            return make_response("Invalid request, body data.", 400)
        
        result = postBot(jsonData)
        
        return make_response("result: " + result.result, 201)
