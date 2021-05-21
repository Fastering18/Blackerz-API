from flask_restful import Resource
from flask import jsonify, make_response, request, abort
import time, math, requests
from threading import Timer, Thread
from src.util.database import notifyChanges, mongoDB

from firebase import firebase

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
# MongoClient = mongopy.MongoClient("mongodb+srv://FirstUser:koliman12345@firstcluster.mksml.mongodb.net/FirstDB?retryWrites=true&w=majority")

error1 = {'error': "Invalid body data request, read our documentation for details", 'status': "Not success"}
error2 = {'error': "Failed to update bot data", 'status': "Not success"}
error3 = {'error': "shortDescription too long, must lower than 50 characters length!", 'status': "Not success"}
error4 = {'error': "Bot not found, you can only edit the existing bot!", 'status': "Not success"}
error5 = {'error': "longDescription too long, must lower than 4000 characters length!", 'status': "Not success"}
error6 = {'error': "prefix too long! must lower than 5 characters length and 1 minimum", 'status': "Not success"}
error7 = {'error': "prefix must be not empty!", 'status': "Not success"}
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
        if 'prefix' in data and self.result == None:
            if len(data['prefix']) > 5:
                self.result = error6
                return 
            if data['prefix'] == "":
                self.result = error7
                return 
            firebaseDB.put('/Infrastructure/botlist/' + id, "prefix", data['prefix'])
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
    isOwner = mongoDB().is_ownerof(auth=clientAuthV1, tipe="botlist", aset=str(id)) #verifyItemOwner(clientAuthV1, str(id))
    
    if isOwner["success"] == False:
       return make_response(jsonify(isOwner["reason"]), 401) 
    if not jsonData:
       return make_response(jsonify(error1), 400)
    if isinstance(jsonData.get('ShortDescription'), str) and int(len(jsonData['ShortDescription'])) > 120:
       return make_response(jsonify(error3), 400)
    if isinstance(jsonData.get('LongDescription'), str) and int(len(jsonData['ShortDescription'])) > 4000:
       return make_response(jsonify(error5), 400)
    jsonData["id"] = str(id)
    botum, result = mongoDB().uploadBot(id=id, data={
        "name": jsonData.get("name"),
        "avatar": jsonData.get("avatar"),
        "prefix": jsonData.get("prefix"),
        "ShortDescription": jsonData.get("shortDescription"),
        "LongDescription": jsonData.get("longDescription"),
        "serverCount": jsonData.get("serverCount"),
        "tags": (isinstance(jsonData.get("tags"), list) and len(jsonData["tags"]) < 6) and jsonData.get("tags") or None
    })  #edit(jsonData, str(id))
    
    if result["sucess"] == True:
        Thread(target=notifyChanges, args=["<@{0}> edited bot <@{1}>\n  \>> {2}bots/{1}".format(isOwner.get("user").get('id'), str(id), request.url_root), id]).start()
        return make_response(jsonify(result), 201, {'Content-Type': 'application/json'})
    else: 
        return make_response(jsonify(result), 400, {'Content-Type': 'application/json'})
    
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
        isOwner = mongoDB().is_ownerof(auth=clientAuthV1, tipe="botlist", aset=str(id)) #verifyItemOwner(clientAuthV1, str(id))
        jsonData = request.get_json()
        
        if isOwner["success"] == False:
           return make_response(jsonify(isOwner["reason"]), 401) 
    
        print(jsonData or request.data)
        if not jsonData or not jsonData.get("servercount"):
           return make_response(jsonify(error1), 400, {'Content-Type': 'application/json'})
        
        botum, result = mongoDB().uploadBot(id=id, data={"serverCount": jsonData.get("servercount")})  #edit({"serverCount": jsonData.get("servercount")}, str(id))
        
        if result["sucess"] == True:
            return make_response(jsonify(result), 201, {'Content-Type': 'application/json'})
        else: 
            return make_response(jsonify(result), 400, {'Content-Type': 'application/json'})
