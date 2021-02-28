from flask_restful import Resource, reqparse
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time, json, requests, os, random, string
from threading import Timer

from firebase import firebase

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
OAUTH2_REDIRECT_URI = 'https://blackerz.herokuapp.com/api/v1/discord/callback'
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

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

def verifyHCaptcha(response=None, remote_ip=None, client=None):
    if client == None or "username" in client:
        return False
    data = {
            "secret": "0x1a92Fc4CD3367d965aa5ffb3B5107710f5a7e0D6",
            "response": response or request.form.get('h-captcha-response'),
            "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
            }
    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    return r.json()["success"] if r.status_code == 200 else False

def token_updater(token):
    session['oauth2_token'] = token
def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)
def generateRandomKey(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str
def generateAuthorizationV1():
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(random.randint(21, 24)))
    return result_str
        
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
        discord = make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        print(user)
        if verifyHCaptcha(client=user) == False:
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
