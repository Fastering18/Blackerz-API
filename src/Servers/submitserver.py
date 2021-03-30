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
def verifyItemOwner(authV1, botId, tipe="botlist"):
    if authV1 == None: return {"success": False, "reason": "Unauthorized, Please put Authoriation headers"}
    user = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/WebUsers.json?orderBy="AuthorizationV1"&equalTo="{authV1}"')
    user = user.json()
    isUserExist = len(list(user.keys())) > 0
    if not isUserExist: return {"success": False, "reason": "Unauthorized, User doesnt exist"}
    user = list(user.keys())[0]
    item = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/{tipe}.json?orderBy="owner/id"&equalTo="{user}"')
    item = item.json()
    isBotOwned = item.get(botId)
    if isBotOwned == None: return {"success": False, "reason": "Unauthorized"}
    return {"success": True, "id": user}

class serverManager():
    def __init__(self, id):
        self.result = {'error': None, 'status': "sucess", 'code': 201}
        self.id = id
        
    def submitServer(self, dataREQ):
        if ("icon" in dataREQ and isinstance(dataREQ['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + self.id + '/' + dataREQ['icon']) == False): 
            self.result = {'error': "icon url returned 404 (not found)", 'status': "failed", 'code': 400};
            return self
        if ("ShortDescription" in dataREQ and isinstance(dataREQ['ShortDescription'], str) and len(dataREQ['ShortDescription']) > 120): 
            self.result = {'error': "ShortDescription must lower than 120 characters length!", 'status': "failed", 'code': 400};
            return self
        
        firebaseDB.put('/Infrastructure/serverlist/' + self.id, "name", dataREQ['name'])
        firebaseDB.put('/Infrastructure/serverlist/' + self.id, "owner", {
                    'id': dataREQ['owner']['id'],
                    'name': dataREQ['owner']['name']
                })
        if ("memberCount" in dataREQ):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "memberCount", dataREQ['memberCount'])
        serverinfo = firebaseDB.get('/Infrastructure/serverlist/' + self.id, None)
        
        if not "upvotes" in serverinfo:
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "upvotes", 0)    
        if ("ShortDescription" in dataREQ and isinstance(dataREQ['ShortDescription'], str) and len(dataREQ['ShortDescription']) < 120):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "ShortDescription", dataREQ['ShortDescription'])
        if ("icon" in dataREQ and isinstance(dataREQ['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + dataREQ['id'] + '/' + dataREQ['icon']) == True):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "icon", dataREQ['icon'])
        if ("joinLink" in dataREQ) and (dataREQ["joinLink"] != ""):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "joinLink", dataREQ['joinLink'])
              
        return self
            
    def editServer(self, dataREQ):
        if ("icon" in dataREQ and isinstance(dataREQ['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + self.id + '/' + dataREQ['icon']) == False): 
            self.result = {'error': "icon url returned 404 (not found)", 'status': "failed", 'code': 400};
            return self
        if ("ShortDescription" in dataREQ and isinstance(dataREQ['ShortDescription'], str) and len(dataREQ['ShortDescription']) > 120): 
            self.result = {'error': "ShortDescription must lower than 120 characters length!", 'status': "failed", 'code': 400};
            return self
        
        serverinfo = firebaseDB.get('/Infrastructure/serverlist/' + self.id, None)
        if serverinfo == None:
            self.result = {'error': "Server doesn't exist", 'status': "failed", 'code': 404}
            return self
        if ("name" in dataREQ):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "name", dataREQ['name'])
        if ("owner" in dataREQ and "id" in dataREQ['owner'] and "name" in dataREQ['owner']):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "owner", {
                'id': dataREQ['owner']['id'],
                'name': dataREQ['owner']['name']
            })
        if ("memberCount" in dataREQ):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "memberCount", dataREQ['memberCount'])
        if not "upvotes" in serverinfo:
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "upvotes", 0)
            
        if ("shortDescription" in dataREQ and isinstance(dataREQ['shortDescription'], str) and len(dataREQ['ShortDescription']) < 60):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "ShortDescription", dataREQ['ShortDescription'])
         if ("longDescription" in dataREQ and isinstance(dataREQ['longDescription'], str) and len(dataREQ['longDescription']) < 4000):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "LongDescription", dataREQ['longDescription'])
        if ("icon" in dataREQ and isinstance(dataREQ['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + dataREQ['id'] + '/' + dataREQ['icon']) == True):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "icon", dataREQ['icon'])
        if ("joinLink" in dataREQ) and (dataREQ["joinLink"] != ""):
            firebaseDB.put('/Infrastructure/serverlist/' + self.id, "joinLink", dataREQ['joinLink'])
        
        return self
        

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
        data = serverManager(str(jsonData["id"])).submitServer(jsonData)
        if data.result["error"] != None:
            return make_response(jsonify(data.result), 400)
        
        return make_response(jsonify(data.result), 201)

class editServer(Resource):
    def put(self, id):
        jsonData = request.get_json()
        clientAuthV1 = request.headers.get('Authorization')
        isOwner = verifyItemOwner(clientAuthV1, str(id), tipe="serverlist")
        if isOwner["success"] == False:
            return make_response(jsonify(isOwner["reason"]), 401) 
        if not jsonData:
           return make_response(jsonify(error1), 400)
        if 'shortDescription' in jsonData and int(len(jsonData['shortDescription'])) > 120:
           return make_response(jsonify(error3), 400)
        if 'longDescription' in jsonData and int(len(jsonData['longDescription'])) > 4000:
           return make_response(jsonify(error5), 400)
    
        server_edit = serverManager(str(id)).editServer(jsonData)
        #if server_edit.result['error'] != None:
            #return make_response(jsonify(server_edit.result), server_edit.result['code'])
        
        return make_response(jsonify(server_edit.result), server_edit.result['code'])
        
    
