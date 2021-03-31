from flask_restful import Resource, reqparse
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time, json, requests, os, random, string
from threading import Timer, Thread
import util.database as databaseManager

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
nouserquery = {'error': 'Please insert "?user=[USER_ID]" parameter to check user', 'status': "Not success"}

def identifyVoter(clientID, code):
    result = firebaseDB.get('/Infrastructure/WebUsers/' + clientID, None)
    if result and "code" in result and result["code"] == code:
        return result
    else:
        return None

def verifyHCaptcha(response=None, remote_ip=None, client=None):
    if client == None or not "username" in client:
        return {"success": False, "reason": "notlogined"}
    data = {
            "secret": "0x1a92Fc4CD3367d965aa5ffb3B5107710f5a7e0D6",
            "response": response or request.form.get('h-captcha-response'),
            "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
            }
    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    return {"success": r.json()["success"] if r.status_code == 200 else False, "reason": "invalidcaptcha"}

def verifyOwner(authV1, botId, tipe="botlist"):
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
    #except:
        #return {"success": False, "reason": "Unauthorized, failed to identify"}

def checkVote(userId, itemId, tipe="botVotes"):
    try:
        result = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/Votes/{tipe}/{itemId}/{userId}.json').json()
        currentTime = time.time() * 1000    #to JavaScript timestamps
        voted = result != None and ((int(currentTime) - int(result)) <= 0)
        return {"voted": int(voted), "lastVote": int(result)} if voted else {"voted": 0, "lastVote": result}
    except:
        return {"voted": 0, "lastVote": "null"}
                       
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
    def __init__(self, botID, client, tipe):
        path = '/Infrastructure/Votes/'+ tipe +'/' + str(botID) + "/" + client["id"]
        clientVote = firebaseDB.get(path, None)
        print(clientVote)
        currentTime = time.time() * 1000    #to JavaScript timestamps
        if (clientVote == None) or (int(currentTime) - int(clientVote) >= 0):
            botData = firebaseDB.get('/Infrastructure/botlist/' + str(botID), None) if tipe == "botVotes" else firebaseDB.get('/Infrastructure/serverlist/' + str(botID), None)
            firebaseDB.put('/Infrastructure/Votes/'+ tipe +'/' + str(botID), client["id"], currentTime + 4.32e+7)
            
            currentVotes = int(botData["upvotes"])
            currentVotes += 1
            result = firebaseDB.put('/Infrastructure/botlist/' + str(botID), "upvotes", currentVotes) if tipe == "botVotes" else firebaseDB.put('/Infrastructure/serverlist/' + str(botID), "upvotes", currentVotes)
            self.result = result
        else:
            self.result = None
            self.canVoteTime = 4.32e+7 - (int(currentTime) - int(clientVote))
             
class voteBot(Resource):
    # PRIVATE BOT VOTE, with hcaptcha
    
    def post(self, id):
        if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))
        discord = make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        isVerified = verifyHCaptcha(client=user)
        if isVerified["success"] == False:
            return redirect(f"{request.url_root}bots/{id}/vote?err={isVerified['reason']}")
        
        vote = addVote(id, user, "botVotes")
        if vote.result == None:
            return redirect(f"{request.url_root}bots/{id}/vote?err=alreadyvoted", code=301)
        else: 
            Thread(target=databaseManager.notifyWebhook, args=[id, user["id"]]).start()
            return redirect(f"{request.url_root}bots/{id}", code=301) # make_response(jsonify({success: True}), 201) #vote.result
        
    def put(self, id):
        if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))
        discord = make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        isVerified = verifyHCaptcha(client=user)
        if isVerified["success"] == False:
            return make_response(jsonify({"success": False, "error": isVerified['reason']}), 401)
        
        vote = addVote(id, user, "botVotes")
        if vote.result == None:
            return make_response(jsonify({"success": False, "error": "already voted, wait 12 hours later"}), 400)
        else:
            Thread(target=databaseManager.notifyWebhook, args=[id, user["id"]]).start()
            return make_response(jsonify({"success": True, "error": "none"}), 201)
                            
class publicVoteApiBot(Resource):
    # PUBLIC CHECK VOTE BOT 
    def get(self, id):
        if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))      
        userToCheck = request.values.get("user")
        if userToCheck == None:
            return make_response(jsonify(nouserquery), 400)
        clientAuthV1 = request.headers.get('Authorization')
        isOwner = verifyOwner(clientAuthV1, str(id))
                            
        if isOwner["success"] != True:
           return make_response(jsonify(isOwner["reason"]), 401) 
        
        return make_response(jsonify(checkVote(userToCheck, str(id))), 200)
                            
class voteServer(Resource):
    # PRIVATE SERVER VOTE, with hcaptcha
    def post(self, id):                               
       if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))
       discord = make_session(token=session.get('oauth2_token'))
       user = discord.get(API_BASE_URL + '/users/@me').json()
       isVerified = verifyHCaptcha(client=user)
       if isVerified["success"] == False:
           return redirect(f"https://blackerz.herokuapp.com/servers/{id}/vote?err={isVerified['reason']}")
        
       vote = addVote(id, user, "serverVotes")  
       if vote.result == None:
           return redirect(f"{request.url_root}servers/{id}/vote?err=alreadyvoted", code=301)
       else: 
           return redirect(f"{request.url_root}servers/{id}", code=301)                
    
    def get(self, id):
       if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))      
       code = request.values.get("user")
       if code == None:
            return make_response(jsonify(nouserquery), 400)
       clientAuthV1 = request.headers.get('Authorization')
       isOwner = verifyOwner(clientAuthV1, id, "serverlist")
                            
       if isOwner["success"] != True:
           return make_response(jsonify(isOwner["reason"]), 401) 
        
       return make_response(jsonify(checkVote(isOwner["id"], id, "serverVotes")), 200)

class publicVoteApiServer(Resource):
    # PUBLIC CHECK VOTE SERVER                        
    def get(self, id):
       if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))      
       userToCheck = request.values.get("user")
       if userToCheck == None:
            return make_response(jsonify(nouserquery), 400)
       clientAuthV1 = request.headers.get('Authorization')
       isOwner = verifyOwner(clientAuthV1, str(id), "serverlist")
                            
       if isOwner["success"] != True:
           return make_response(jsonify(isOwner["reason"]), 401) 
        
       return make_response(jsonify(checkVote(userToCheck, str(id), "serverVotes")), 200)                           
