from flask_restful import Resource, reqparse
from flask import jsonify, make_response, request, abort
import time
import json
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
        
class addVote():
    def __init__(self, botID, client):
        clientVote = firebaseDB.get('/Infrastructure/Votes/botVotes/' + botID + "/" + client["id"], None)
        currentTime = time.time() * 1000    #to JavaScript timestamps
        if (clientVote == None) or (int(currentTime) - int(clientVote) >= 4.32e+7):
            botData = firebaseDB.get('/Infrastructure/botlist/' + botID, None)
            firebaseDB.put('/Infrastructure/Votes/botVotes/' + botID, client["id"], currentTime)
            
            currentVotes = int(botData["upvotes"])
            currentVotes += 1
            result = firebaseDB.put('/Infrastructure/botlist/' + botID, "upvotes", currentVotes)
            self.result = result
        else:
            self.result = None
            self.canVoteTime = 4.32e+7 - (currentTime - clientVote)
             
class voteBot(Resource):
    def post(self, id):
        clientID = request.headers.get('clientId')
        clientCode = request.headers.get('code')
        if (not clientID) and (not clientCode):
            return make_response(jsonify(unauthorizedAcess), 401)
        if not clientID:
            return make_response(jsonify(unauthorizedAcess1), 401)
        if not clientCode:
            return make_response(jsonify(unauthorizedAcess2), 401)
            
        voter = identifyVoter(clientID, clientCode)
        if voter == None:
            return make_response(jsonify(unauthorizedAcess3), 401)    
            
        voter["id"] = clientID    
        vote = addVote(id, voter)
        if vote.result == None:
            warnVote = forbiddenAcess1
            warnVote['error'] = "Already voted, you can vote again in: " + str(int(vote.canVoteTime)) + " seconds later."
            return make_response(jsonify(warnVote), 401)   
        else: 
            return make_response(jsonify(vote.result), 201)
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
            return make_response(jsonify(warnVote), 401)   
        else: 
            return make_response(jsonify(vote.result), 201)
