from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request, abort
import time
import json
import requests
from threading import Timer

from firebase import firebase

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

error1 = {'error': "Invalid body data request, read our documentation for details", 'status': "Not success"}
unauthorizedAcess = {'error': "Unauthorized Acess, input clientId and code in headers.", 'status': "Not success"}
unauthorizedAcess1 = {'error': "Unauthorized Acess, clientId not found in headers.", 'status': "Not success"}
unauthorizedAcess2 = {'error': "Unauthorized Acess, code not found in headers.", 'status': "Not success"}
unauthorizedAcess3 = {'error': "Unauthorized Acess, client not found, please input correct clientId and code in headers.", 'status': "Not success"}
forbiddenAcess1 = {'status': "Not success"}

def identifyVoter(clientID, code):
    result = firebaseDB.get('/Infrastructure/WebUsers/' + clientID, None)
    if result and "code" in result and result["code"] == code:
        return result
    else:
        return None

def verifyHCaptcha(response=None, remote_ip=None):
    data = {
            "secret": "0x1a92Fc4CD3367d965aa5ffb3B5107710f5a7e0D6",
            "response": response or request.form.get('h-captcha-response'),
            "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
            }
    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    return r.json()["success"] if r.status_code == 200 else False
        
class addVote():
    def __init__(self, botID, client):
        clientVote = firebaseDB.get('/Infrastructure/Votes/botVotes/' + str(botID) + "/" + client["id"], None)
        currentTime = time.time() * 1000    #to JavaScript timestamps
        if (clientVote == None) or (int(currentTime) - int(clientVote) >= 0):
            botData = firebaseDB.get('/Infrastructure/botlist/' + str(botID), None)
            firebaseDB.put('/Infrastructure/Votes/botVotes/' + str(botID), client["id"], currentTime + 4.32e+7)
            
            currentVotes = int(botData["upvotes"])
            currentVotes += 1
            result = firebaseDB.put('/Infrastructure/botlist/' + str(botID), "upvotes", currentVotes)
            self.result = result
        else:
            self.result = None
            self.canVoteTime = 4.32e+7 - (int(currentTime) - int(clientVote))
             
class voteBot(Resource):
    def post(self, id):
        if verifyHCaptcha() == False:
            return make_response(jsonify(warnVote), 401)   
        #clientID = request.headers.get('clientId')
        #clientCode = request.headers.get('code')
        #if (not clientID) and (not clientCode):
            #return make_response(jsonify(unauthorizedAcess), 401)
        #if not clientID:
            #return make_response(jsonify(unauthorizedAcess1), 401)
        #if not clientCode:
            #return make_response(jsonify(unauthorizedAcess2), 401)
            
        #voter = identifyVoter(clientID, clientCode)
        #if voter == None:
            #return make_response(jsonify(unauthorizedAcess3), 401)    
            
        #voter["id"] = clientID    
        #vote = addVote(id, voter)
        #if vote.result == None:
            #warnVote = forbiddenAcess1
            #warnVote['error'] = "Already voted, you can vote again in: " + str(int(vote.canVoteTime)) + " seconds later."
            #return make_response(jsonify(warnVote), 401)   
        #else: 
        return make_response(jsonify("what a yes"), 201) #vote.result
    def put(self, id):
        clientID = request.headers.get('clientId')
        clientCode = request.headers.get('code')
        if (not clientID) and (not clientCode):
            return make_response(jsonify(unauthorizedAcess), 401)
        if not clientID:
            return make_response(jsonify(unauthorizedAcess1), 401)
        if not clientCode:
            return make_response(jsonify(unauthorizedAcess2), 401)
        
        print(clientID)    
        voter = identifyVoter(clientID, clientCode)
        if voter == None:
            return make_response(jsonify(unauthorizedAcess3), 401)    
            
        voter["id"] = clientID    
        vote = addVote(id, voter)
        if vote.result == None:
            warnVote = forbiddenAcess1
            warnVote['error'] = "Already voted, you can vote again in: " + str(int(vote.canVoteTime)) + " seconds later."
            return make_response(jsonify(warnVote), 403)   
        else: 
            return make_response(jsonify(vote.result), 201)
