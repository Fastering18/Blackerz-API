from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request, abort
import time
import json
import requests
from threading import Timer

from firebase import firebase

timeStamp = 0

error1 = {'error': "Invalid body data request, read our documentation for details", 'status': "Not success"}
unauthorizedAcess1 = {'error': "Unauthorized Acess, tidak terdapat api key.", 'status': "Not success"}
unauthorizedAcess2 = {'error': "Unauthorized Acess, api key yang di inputkan salah, kontak developer untuk mendapatkan api key.", 'status': "Not success"}

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

def identifyAPiKey(apiKey):
    result = firebaseDB.get('/Infrastructure/Users/' + apiKey, None)
    return result
def isLinkExist(link):
    exist = requests.get(link)
    return exist.status_code != 404 
class postBot():
    def __init__(self, dataREQ):
        firebaseDB.put('/Infrastructure/serverlist/' + dataREQ['id'], "name", dataREQ['name'])
        firebaseDB.put('/Infrastructure/serverlist/' + dataREQ['id'], "owner", {
                    'id': dataREQ['owner']['id'],
                    'name': dataREQ['owner']['name']
                })
        if ("memberCount" in dataREQ):
            firebaseDB.put('/Infrastructure/serverlist/' + dataREQ['id'], "memberCount", dataREQ['memberCount'])
        serverinfo = firebaseDB.get('/Infrastructure/serverlist/' + dataREQ['id'], None)
        
        if not "upvotes" in serverinfo:
            firebaseDB.put('/Infrastructure/serverlist/' + dataREQ['id'], "upvotes", 0)    
        if ("ShortDescription" in dataREQ and isinstance(dataREQ['ShortDescription'], str) and len(dataREQ['ShortDescription']) < 60):
            firebaseDB.put('/Infrastructure/serverlist/' + dataREQ['id'], "ShortDescription", dataREQ['ShortDescription'])
        if ("icon" in dataREQ and isinstance(dataREQ['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + dataREQ['id'] + '/' + dataREQ['icon']) == True):
            firebaseDB.put('/Infrastructure/serverlist/' + dataREQ['id'], "icon", dataREQ['icon'])
        if ("joinLink" in dataREQ) and (dataREQ["joinLink"] != ""):
            firebaseDB.put('/Infrastructure/serverlist/' + dataREQ['id'], "joinLink", dataREQ['joinLink'])
        
        self.result = {'error': None, 'status': "sucess"}
        if ("icon" in dataREQ and isinstance(dataREQ['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + dataREQ['id'] + '/' + dataREQ['icon']) == False) : self.result = {'error': "icon url 404 not found", 'status': "failed"};
        if ("ShortDescription" in dataREQ and isinstance(dataREQ['ShortDescription'], str) and len(dataREQ['ShortDescription']) > 60) : self.result = {'error': "ShortDescription must lower than 60 characters length!", 'status': "failed"};

class postServer(Resource):
    def post(self, id):
        jsonData = request.get_json()
        apiKey = request.headers.get('apiKey')
        if not apiKey:
            return make_response(jsonify(unauthorizedAcess1), 401)
        if identifyAPiKey(apiKey) == None: 
            return make_response(jsonify(unauthorizedAcess2), 401)
        
        print(jsonData)
        if (not jsonData) or (not 'name' in jsonData) or (not 'owner' in jsonData) or (not 'memberCount' in jsonData) or (not 'id' in jsonData['owner']) or (not 'name' in jsonData['owner']) or (isinstance(jsonData["memberCount"], int) != True):
            return make_response(jsonify(error1), 400)
        if (not "id" in jsonData) and id:
            jsonData["id"] = id
            
        jsonData["id"] = str(jsonData["id"])    
        result = postBot(jsonData)
        if "result" in result and "error" in result.result and result.result.error != None:
            return make_response(jsonify(result.result), 400)
        
        return make_response(jsonify(result.result), 201)
