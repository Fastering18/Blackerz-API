from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request, abort
import time
import json
from threading import Timer

from firebase import firebase

timeStamp = 0

error1 = {'error': "Invalid body data request, read our documentation for details", 'status': "Not success"}
unauthorizedAcess = {'error': "Unauthorized Acess, please provide Api Key", 'status': "Not success"}

firebaseDB = firebase.FirebaseApplication(
    'https://blackerz-default-rtdb.firebaseio.com/', None)

def identifyAPiKey(apiKey):
    result = firebaseDB.get('/Infrastructure/Users/' + apiKey, None)
    print(result)
    return result

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
        firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "name", dataREQ['name'])
        firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "owner", {
                    'id': dataREQ['owner']['id'],
                    'name': dataREQ['owner']['name']
                })
        firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "tag", dataREQ['tag'])
        firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "upvotes", 0)
        
        if "avatar" in dataREQ:
            firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "avatar", dataREQ['avatar'])
        if "inviteLink" in dataREQ:
            firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "inviteLink", dataREQ['inviteLink'])
        
        self.result = {'error': None, 'status': "sucess"}

class resource3(Resource):
    def post(self, id):
        jsonData = request.get_json()
        apiKey = request.headers.get('apiKey')
        identifyAPiKey(apiKey)
        
        if not apiKey or not apiKey == "anjirbangjago500eaaApiDEV001njir": 
            return make_response(jsonify(unauthorizedAcess), 401)
        
        if not jsonData or not 'name' in jsonData or not 'owner' in jsonData or not 'tag' in jsonData or not 'id' in jsonData['owner'] or not 'name' in jsonData['owner']:
            return make_response(jsonify(error1), 400)
        
        result = postBot(jsonData)
        
        return make_response(jsonify(result.result), 201)
