from flask_restful import Resource
from flask import jsonify, make_response, Markup
import time, requests, markdown
from threading import Timer

from firebase import firebase

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
    servers = data("getserver", id)
    server = servers.data
    
    if server != None:
        if "LongDescription" in server:
            server["LongDescription"] = Markup(markdown.markdown(server["LongDescription"]))
        return make_response(jsonify(server), 200)
    else: 
        return make_response(jsonify(error1), 404)
