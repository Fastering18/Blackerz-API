from flask_restful import Resource
from flask import jsonify, make_response, render_template, session, request, redirect
import time, json, requests
from threading import Timer, Thread
from src.util.database import mongoDB
from bson.json_util import dumps

from firebase import firebase

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
queryBotCaches = {}
firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

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

timeStamp = 0
error1 = {'error': "Bot not found", 'status': "Not success"}

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
            self.result = mongoDB().botQuerySearch(kueri=str(self.keyword)) #requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy="{self.filter}"&limitToLast={self.limit}').json()
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
