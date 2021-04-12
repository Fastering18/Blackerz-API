from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request, abort
import time, json
from threading import Timer
from src.util.database import mongoDB, IdentifyApiUser

from firebase import firebase

timeStamp = 0

error1 = {'error': "Invalid body data request, read our documentation for details", 'status': "Not success"}
unauthorizedAcess1 = {'error': "Unauthorized Acess, tidak terdapat api key.", 'status': "Not success"}
unauthorizedAcess2 = {'error': "Unauthorized Acess, api key yang di inputkan salah, kontak developer untuk mendapatkan api key.", 'status': "Not success"}

firebaseDB = firebase.FirebaseApplication(
    'https://blackerz-default-rtdb.firebaseio.com/', None)

def identifyAPiKey(apiKey):
    result = firebaseDB.get('/Infrastructure/Users/' + apiKey, None)
    return result

class postBot():
    def __init__(self, dataREQ):
        dataFinal = {
            'name': dataREQ['name'],
             'owner': {
                 'id': dataREQ['owner']['id'],
                 'name': dataREQ['owner']['name']
             },
             'tag': dataREQ['tag'],
             #'upvotes': 0
        }
        #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "name", dataREQ['name'])
        #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "owner", {
                    #'id': dataREQ['owner']['id'],
                    #'name': dataREQ['owner']['name']
                #})
        #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "tag", dataREQ['tag'])
        #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "upvotes", 0)
        #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "prefix", dataREQ['prefix'])
        #if "avatar" in dataREQ:
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "avatar", dataREQ['avatar'])
        #if "inviteLink" in dataREQ:
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['id'], "inviteLink", dataREQ['inviteLink'])
        
        self.result = {'error': None, 'status': "sucess"}

class resource3(Resource):
    def post(self, id):
        jsonData = request.get_json()
        apiKey = request.headers.get('apiKey')
        if not apiKey:
            return make_response(jsonify(unauthorizedAcess1), 401)
        ApiUser = IdentifyApiUser(apikey=apiKey).get_user()
        if not ApiUser.izin.get("postbot") and not ApiUser.izin.get("all"): 
            return make_response(jsonify(unauthorizedAcess2), 401)
        
        if not jsonData or not 'name' in jsonData or not 'owner' in jsonData or not 'tag' in jsonData or not 'id' in jsonData['owner'] or not 'name' in jsonData['owner'] or not 'prefix' in jsonData:
            return make_response(jsonify(error1), 400)
        
        result = postBot(jsonData)
        
        return make_response(jsonify(result.result), 201)
