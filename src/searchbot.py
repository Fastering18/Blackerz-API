from flask_restful import Resource
from flask import jsonify, make_response, render_template, g, session, request, redirect
import time, json, requests, os, random, string
from threading import Timer

from firebase import firebase

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"

class data():
    def __init__(self, dataName, id):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
        if result != None:       
            url = "https://discord.com/api/v8/users/" + str(id)
            r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
            response = r.json() 
            print(response)
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
            self.data = result
            self.timeStamp = time.time()
        else:
            self.data = None

timeStamp = 0
error1 = {'error': "Bot not found", 'status': "Not success"}

class querySearch:
    def __init__(self, query, dataName):
        self.warns = None
        self.error = False
        self.keyword = query.get("q") or query.get("query") or query.get("kueri")
        self.filter = query.get("sort") or query.get("filter") or query.get("urut")
        if self.keyword and self.keyword.strip().length <= 0: 
            self.warns = {"error": True, "message": 'Invalid \'q\' query, cannot empty', "code": 400}
            return
        if self.filter and self.filter != "upvotes": 
            self.warns = {"error": True, "message": 'Invalid \'filter\' query', "code": 400}
            return
        try:
            self.result = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy="AuthorizationV1"&equalTo="{authV1}"')
        except:
            self.error = True
            
class resouce(Resource):
  def get(self, id):
    botum = data("getbot", id)
    bot = botum.data
    
    if bot != None:
        return make_response(jsonify(bot), 200)
    else: 
        return make_response(jsonify(error1), 404)
    
 
# SEARCH BASED QUERY
class searchBotQuery(Resource):
  def get(self, id):
    querySearch(request.values)
    
