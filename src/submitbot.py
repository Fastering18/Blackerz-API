from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request, abort
import time
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
        data = {'name': dataREQ.name,
                'owner': {
                    'id': dataREQ.author.id,
                    'name': dataREQ.author.name
                },
                'tag': dataREQ.tag,
                'upvotes': 0
                }
        self.result = firebaseDB.post('/Infrastructure/botlist/' + dataREQ.id, data, {'print': 'pretty'}, {'X_FANCY_HEADER': 'VERY FANCY'})


class resource3(Resource):
    def post(self, id):
        print(request.form)
        if not request.json or not 'name' in request.json or not 'owner' in request.json:
            return make_response("Invalid request, body data.", 400)
        print(request.json)
        result = postBot(request.json)
        
        return make_response("result: " + result.result, 201)
