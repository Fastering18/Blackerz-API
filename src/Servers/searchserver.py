from flask_restful import Resource
from flask import jsonify, make_response, Markup, request
import time, markdown
from threading import Timer
from firebase import firebase
from src.util.database import mongoDB
from bson.json_util import dumps

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

class data():
    def __init__(self, dataName, id):
        result = firebaseDB.get('/Infrastructure/serverlist/' + str(id), None)
        if result != None:       
            self.data = result
            self.timeStamp = time.time()
        else:
            self.data = None

timeStamp = 0
error1 = {'error': "Server not found", 'status': "Not success"}
        
class findServer(Resource):
  def get(self, id):
    #servers = data("getserver", id)
    server = mongoDB().get_server(id=str(id))
    
    if server != None:
        if "LongDescription" in server:
            server["LongDescription"] = Markup(markdown.markdown(server["LongDescription"]))
        return make_response(dumps(server), 200, {'Content-Type': 'application/json'})
    else: 
        return make_response(jsonify(error1), 404, {'Content-Type': 'application/json'})

class autocorrectServer(Resource):
  def get(self):
     kueri = request.values.get("query") or request.values.get("kueri") or request.values.get("q")
     if not kueri:
        return make_response(jsonify({"error": "no `query` parameter"}), 400, {'Content-Type': 'application/json'})
     res = mongoDB().AutocorrectSearchServer(kueri=kueri)
     return make_response(dumps(res), 200, {'Content-Type': 'application/json'})
        
