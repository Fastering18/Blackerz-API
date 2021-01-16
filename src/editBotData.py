from flask_restful import Resource
from flask import jsonify, make_response
import time
from threading import Timer

from firebase import firebase

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

error1 = {'error': "Invalid body data request, read our documentation for details", 'status': "Not success"}
error2 = {'error': "Failed to update bot data", 'status': "Not success"}
sucess = {'error': "null", 'status': "success"}
unauthorizedAcess = {'error': "Unauthorized Acess, please provide correct owner credentials", 'status': "Not success"}

class edit(data):
    def __init__(self, data):
         if name in data:
             firebaseDB.put('/Infrastructure/botlist/' + data['id'], "name", data['name'])
         if avatar in data:
             firebaseDB.put('/Infrastructure/botlist/' + data['id'], "avatar", data['avatar'])
         if shortDescription in data:
             firebaseDB.put('/Infrastructure/botlist/' + data['id'], "ShortDescription", data['shortDescription'])
         self.result = True

def verifyOwner(clientId, code):
    result = firebaseDB.get('/Infrastructure/WebUsers/'+ clientId, None)
    if result == None:
        return False
    if not "code" in result or result["code"] != code:
        return False
    return True         

class resouce(Resource):
  def put(self, id):
    jsonData = request.get_json()
    clientId = request.headers.get('clientId')
    clientCode = request.headers.get('code')
        
    if verifyOwner(clientId, clientCode) == False: 
       return make_response(jsonify(unauthorizedAcess), 401)
    if not jsonData or not 'id' in jsonData:
       return make_response(jsonify(error1), 400)
    botum = edit(jsonData)
    
    if botum.result == True:
        return make_response(jsonify(sucess), 201)
    else: 
        return make_response(jsonify(error2), 422)
  def post(self, id):
    jsonData = request.get_json()
    clientId = request.headers.get('clientId')
    clientCode = request.headers.get('code')
        
    if verifyOwner(clientId, clientCode) == False: 
       return make_response(jsonify(unauthorizedAcess), 401)
    if not jsonData or not 'id' in jsonData:
       return make_response(jsonify(error1), 400)
    botum = edit(jsonData)
    
    if botum.result == True:
        return make_response(jsonify(sucess), 201)
    else: 
        return make_response(jsonify(error2), 422)
