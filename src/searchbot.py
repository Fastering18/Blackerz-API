from flask_restful import Resource
from flask import jsonify, make_response, render_template, session, request, redirect
import time, json, requests
from threading import Timer, Thread
from src.util.database import mongoDB, IdentifyApiUser, notifyChanges
from bson.json_util import dumps

from firebase import firebase

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
queryBotCaches = {}
firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
error1 = {'error': "Bot not found", 'status': "Not success"}
unauthorizedAcess1 = {'error': "Unauthorized Acess, tidak terdapat api key.", 'status': "Not success"}
unauthorizedAcess2 = {'error': "Unauthorized Acess, api key yang di inputkan salah, kontak developer untuk mendapatkan api key.", 'status': "Not success"}

def deleteCache(link):
  if not link in queryBotCaches: return False
  del queryBotCaches[link]
  return True

def putCache(link, isi):
    queryBotCaches[link] = isi
    Timer(800.0, deleteCache, [link]).start()
    return True

def updateBotData(id, result):
    url = "https://discord.com/api/v8/users/" + str(id)
    r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
    response = r.json() 
    if "code" in response and response["code"] == 0 : self.data = None; return;
    if "name" in result and "username"in response and result["name"] != response["username"]:
        result["name"] = response["username"]
        result["tag"] = response["username"] + "#" + response["discriminator"]
        firebaseDB.put('/Infrastructure/botlist/' + str(id), "name", response["username"])
        firebaseDB.put('/Infrastructure/botlist/' + str(id), "tag", result["tag"])
    if "avatar" in result and "avatar" in response:
        if result["avatar"] != response["avatar"]:
            result["avatar"] = response["avatar"]
            firebaseDB.put('/Infrastructure/botlist/' + str(id), "avatar", response["avatar"])       
        elif "avatar" in response and not "avatar" in result:
            result["avatar"] = response["avatar"]
            firebaseDB.put('/Infrastructure/botlist/' + str(id), "avatar", response["avatar"])  
  
class data():
    def __init__(self, dataName, id):      
        result = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
        if result != None:
            Thread(target=updateBotData, args=[id, result]).start() 
            self.data = result
            putCache(str(id) + "_bot", self.data)
        else:
            self.data = None

class querySearch:
    def __init__(self, query, dataName="botlist"):
        self.warns = None
        self.error = False
        self.keyword = query.get("q") or query.get("query") or query.get("kueri")
        self.filter = query.get("sort") or query.get("filter") or query.get("urut") or "upvotes"
        self.limit = query.get("limit") or 100
        self.harusSama = query.get("mirip") == "ya" or query.get("mirip") == "iya"
        self.result = {}
        if self.keyword and len(self.keyword.strip()) <= 0: 
            self.warns = {"error": True, "message": 'Invalid \'q\' query, cannot empty', "code": 400}
            return
        if self.filter and self.filter != "upvotes": 
            self.warns = {"error": True, "message": 'Invalid \'filter\' query', "code": 400}
            return
        if isinstance(self.limit, str) and not self.limit.isdigit():
            self.warns = {"error": True, "message": 'Invalid \'limit\' query, must be number', "code": 400}
            return
        try:
            self.result, jmlh = mongoDB().botQuerySearch(kueri=str(self.keyword)) #requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy="{self.filter}"&limitToLast={self.limit}').json()
            #if self.keyword:
                #listres = [] #list(self.result.values())
                #for kunci in self.result:
                    #if self.result[kunci]["name"].lower().startswith(self.keyword.lower()) or (self.harusSama == True and self.keyword.lower() in self.result[kunci]["name"].lower()):
                        #listres.append(self.result[kunci])
                #self.result = listres
            #putCache(str(query), self.result)
        except Exception as kesalahan:
            print(kesalahan)
            self.warns = {"error": True, "message": 'Internal error, this is not your error, please report this issues to github.', "code": 500}
            self.error = True
            
class getBotFromID(Resource):
  def get(self, id):
    #if (str(id) + "_bot") in queryBotCaches: return make_response(jsonify(queryBotCaches[(str(id) + "_bot")]), 200)
    bot = mongoDB().get_bot(id=str(id))
    
    if bot != None:
        return make_response(dumps(bot), 200, {'Content-Type': 'application/json'})
    else: 
        return make_response(jsonify(error1), 404, {'Content-Type': 'application/json'})
    
 
# SEARCH BASED QUERY
class searchBotQuery(Resource):
  def get(self):
    #if str(request.values) in queryBotCaches: return make_response(jsonify(queryBotCaches[str(request.values)]), 200)
    sresult = querySearch(request.values)
    if sresult.warns != None: return make_response(jsonify(sresult.warns), sresult.warns["code"], {'Content-Type': 'application/json'})
    return make_response(dumps(sresult.result), 200, {'Content-Type': 'application/json'})
  
class autocorrectsearch(Resource):
  def get(self):
    kueri = request.values.get("query") or request.values.get("kueri") or request.values.get("q")
    if not kueri:
        return make_response(jsonify({"error": "no `query` parameter"}), 400, {'Content-Type': 'application/json'})       
    res = mongoDB().AutocorrectSearchBot(kueri=kueri)
    return make_response(dumps(res), 200, {'Content-Type': 'application/json'})
    
class deleteBotFromID(Resource):
  def delete(self, id):
    apiKey = request.headers.get('apiKey')
    cauth = request.headers.get('Authorization')
    notify = request.values.get('notify')
    if not apiKey and not cauth:
        return make_response(jsonify(unauthorizedAcess1), 401)
      
    deleter = "0"
      
    if apiKey:
        ApiUser = IdentifyApiUser(apikey=apiKey).get_user()
        if not ApiUser.izin.get("deletebot") and not ApiUser.izin.get("all"): 
            return make_response(jsonify(unauthorizedAcess2), 401)
        deleter = ApiUser.data.get('clientId')
    else:
        print("authv1; ", cauth)
        isOwner = mongoDB().is_ownerof(auth=cauth, tipe="botlist", aset=str(id))
        if isOwner["success"] != True:
            return make_response(jsonify(isOwner["reason"]), 401)
        deleter = isOwner["user"].get("id")
      
    bot = mongoDB().get_bot(id=str(id))
    
    if bot != None:
        deleteres = mongoDB().delete_bot(id=str(id))
        delete_status = deleteres.deleted_count == 1
        if delete_status: Thread(target=notifyChanges, args=["<@{0}> deleted bot <@{1}>\n> {2}bots/{1}".format(deleter, str(id), request.url_root), id]).start()
        
        return make_response(jsonify({"success": delete_status}), 200, {'Content-Type': 'application/json'})
    else: 
        return make_response(jsonify(error1), 404, {'Content-Type': 'application/json'})
