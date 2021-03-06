from flask_restful import Resource
from flask import jsonify, make_response, request, abort
import time, math, requests
from threading import Timer
import pymongo as mongopy

from firebase import firebase

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
# MongoClient = mongopy.MongoClient("mongodb+srv://FirstUser:koliman12345@firstcluster.mksml.mongodb.net/FirstDB?retryWrites=true&w=majority")

error1 = {'error': "Invalid body data request, read our documentation for details", 'status': "Not success"}
error2 = {'error': "Failed to update bot data", 'status': "Not success"}
error3 = {'error': "shortDescription too long, must lower than 50 characters length!", 'status': "Not success"}
error4 = {'error': "Bot not found, you can only edit the existing bot!", 'status': "Not success"}
error5 = {'error': "longDescription too long, must lower than 4000 characters length!", 'status': "Not success"}
sucess = {'error': "null", 'status': "success"}
unauthorizedAcess = {'error': "Unauthorized Acess, please provide correct owner credentials", 'status': "Not success"}

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

class edit():
    def __init__(self, data, id):
        currentBot = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
        self.result = None
        if currentBot == None:
            self.result = error4
            return 
        if 'name' in data and self.result == None:
            firebaseDB.put('/Infrastructure/botlist/' + id, "name", data['name'])
        if 'avatar' in data and self.result == None:
            firebaseDB.put('/Infrastructure/botlist/' + id, "avatar", data['avatar'])
        if 'shortDescription' in data and self.result == None:
            firebaseDB.put('/Infrastructure/botlist/' + id, "ShortDescription", data['shortDescription'])
        if 'longDescription' in data and self.result == None:
            firebaseDB.put('/Infrastructure/botlist/' + id, "LongDescription", data['longDescription'])
        if ('serverCount' in data) and (math.isnan(int(data["serverCount"])) == False) and self.result == None:
            firebaseDB.put('/Infrastructure/botlist/' + id, "serverCount", data['serverCount'])
        if self.result == None:
            self.result = True

def verifyOwner(clientId, code):
    if (not isinstance(clientId, (int, str))) or (not isinstance(code, (int, str))) : return False
    result = firebaseDB.get('/Infrastructure/WebUsers/'+ str(clientId), None)
    if result == None:
        return False
    if ("AuthorizationV1" in result) and (result["AuthorizationV1"] == code):        
        return True
    if (not "code" in result) or (result["code"] != code):
        return False
    return True         

class editData(Resource):
  def put(self, id):
    jsonData = request.get_json()
    clientAuthV1 = request.headers.get('Authorization')
    isOwner = verifyItemOwner(clientAuthV1, str(id))
    
    if isOwner["success"] == False:
       return make_response(jsonify(isOwner["reason"]), 401) 
    if not jsonData:
       return make_response(jsonify(error1), 400)
    if 'shortDescription' in jsonData and int(len(jsonData['shortDescription'])) > 120:
       return make_response(jsonify(error3), 400)
    if 'longDescription' in jsonData and int(len(jsonData['longDescription'])) > 4000:
       return make_response(jsonify(error5), 400)
    jsonData["id"] = str(id)
    botum = edit(jsonData, str(id))
    
    if botum.result == True:
        return make_response(jsonify(sucess), 201)
    else: 
        return make_response(jsonify(botum.result), 400)
    
  def post(self, id):
    jsonData = request.get_json()
    clientId = request.headers.get('clientId')
    clientCode = request.headers.get('code')
    clientAuthV1 = request.headers.get('Authorization')
    authentication = clientCode

    if clientCode == None : authentication = clientAuthV1
    if verifyOwner(clientId, authentication) == False: 
       return make_response(jsonify(unauthorizedAcess), 401)
    if not jsonData:
       return make_response(jsonify(error1), 400)
    if 'shortDescription' in jsonData and int(len(jsonData['shortDescription'])) > 120:
       return make_response(jsonify(error3), 400)
    if 'longDescription' in jsonData and int(len(jsonData['longDescription'])) > 4000:
       return make_response(jsonify(error5), 400)
    jsonData["id"] = str(id)
    botum = edit(jsonData, str(id))
    
    if botum.result == True:
        return make_response(jsonify(sucess), 201)
    else: 
        return make_response(jsonify(botum.result), 400)

class ServerCountManager(Resource):
    def post(self, id):
        if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))
        clientAuthV1 = request.headers.get('Authorization')
        isOwner = verifyItemOwner(clientAuthV1, str(id))
        jsonData = request.get_json()
        
        if isOwner["success"] == False:
           return make_response(jsonify(isOwner["reason"]), 401) 
    
        if not jsonData or not "servercount" in jsonData:
           return make_response(jsonify(error1), 400)
        botum = edit({"serverCount": jsonData.get("servercount")}, str(id))
        
        if botum.result == True:
            return make_response(jsonify(sucess), 201)
        else: 
            return make_response(jsonify(botum.result), 400)
