from flask_restful import Resource, reqparse
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time, json, requests, os, random, string
from threading import Timer, Thread

from firebase import firebase

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
OAUTH2_REDIRECT_URI = 'https://blackerz.herokuapp.com/api/v1/discord/callback'
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

headers = {'Content-Type': 'text/html'}

def verifyOwner(user, botId, tipe="botlist"):
    item = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/{tipe}.json?orderBy="owner/id"&equalTo="{user}"')
    item = item.json()
    isBotOwned = item.get(botId)
    if isBotOwned == None: return {"success": False, "reason": "Unauthorized"}
    return {"success": True, "id": user}
  
def token_updater(token):
    session['oauth2_token'] = token
    
def make_session(token=None, state=None, scope=None, redirectURL="https://blackerz.herokuapp.com/api/v1/discord/callback"):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=redirectURL,
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

class updateData():
    def __init__(self, tipe, **Data):
        if tipe == "postUserStats":
            user = Data.get('user', None)
            self.data = {}
            self.data["tag"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "tag", user["tag"])
            self.data["avatar"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "avatar", user["avatar"])
            # self.data["code"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "code", user["code"])
            self.data["username"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "username", user["username"])
            authV1 = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/AuthorizationV1", None)
            createdAt = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/CreatedAt", None)
            if authV1 == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "AuthorizationV1", generateAuthorizationV1())
            if createdAt == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "CreatedAt", datetime.datetime.now().isoformat())
        elif tipe == "allBot":
            result = firebaseDB.get('/Infrastructure/botlist', None)
            self.data = result
            
def updateUserData(id, tag, username, avatar, code):
    UserData = {
       'client_id': id,
       'tag': tag,
       'username': username,
       'avatar': avatar,
       'code': code
    }
    return updateData("postUserStats", user=UserData).data

class data():
    def __init__(self, dataName, id, client=None):
        if dataName == "botinfo":
            result = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
            if client != None : self.client = firebaseDB.get('/Infrastructure/WebUsers/' + client, None)
            if result != None:
                result["id"] = id
                try:
                    url = "https://discord.com/api/v8/users/" + str(id)
                    r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
                    response = r.json() 
                    if result["name"] != response["username"]:
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
                except:
                    self.data = result
                    self.timeStamp = time.time()
            else:
                self.data = None
        if dataName == "serverinfo":
            result = firebaseDB.get('/Infrastructure/serverlist/' + id, None)
            self.data = result
            
    def getOwner(self, client=None):
        if client != None: 
            self.client = firebaseDB.get('/Infrastructure/WebUsers/' + client, None)
            return self.client
        return None

class EditBotPage(Resource):
    def get(self, id):
        if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))
        discord = make_session(token=session.get('oauth2_token'), redirectURL=request.url_root + "api/v1/discord/callback")
        user = discord.get(API_BASE_URL + '/users/@me').json()
        botum = data("botinfo", id)
        client = None
        
        if botum == None:
            return make_response(render_template('404.html', user=user), 404, headers)
        
        if user and "id" in user and "username" in user:      
            oneTimeCode = generateRandomKey(8)
            userID = user["id"]
            userData = [
               str(userID),
               user["username"] + "#" + user["discriminator"],
               user["username"],
               user["avatar"],
               oneTimeCode
            ]
            Thread(target=updateUserData, args=userData).start()
            client = botum.getOwner(user["id"])
          
        if not "id" in user:
            return make_response(render_template('Unauthorized.html', user=user), 401, headers)
        isOwner = verifyOwner(user["id"], str(id))
        if isOwner["success"] == False:
            return make_response(render_template('Unauthorized.html', user=user), 401, headers) 
        
        return make_response(render_template('EditBotPage.html', clientUser=user, bot=botum.data, clientData=client), 200, headers)
        
class EditServerPage(Resource):
    def get(self, id):
        if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))
        discord = make_session(token=session.get('oauth2_token'), redirectURL=request.url_root + "api/v1/discord/callback")
        user = discord.get(API_BASE_URL + '/users/@me').json()
        servere = data("serverinfo", str(id))
        client = None
        
        if servere == None:
            return make_response(render_template('404.html', user=user), 404, headers)
        
        if user and "id" in user and "username" in user:      
            oneTimeCode = generateRandomKey(8)
            userID = user["id"]
            userData = [
               str(userID),
               user["username"] + "#" + user["discriminator"],
               user["username"],
               user["avatar"],
               oneTimeCode
            ]
            Thread(target=updateUserData, args=userData).start()
            client = servere.getOwner(user["id"])
        
        if not "id" in user:
            return make_response(render_template('Unauthorized.html', user=user), 401, headers)
        isOwner = verifyOwner(user["id"], str(id), tipe="serverlist")
        if isOwner["success"] == False:
            return make_response(render_template('Unauthorized.html', user=user), 401, headers) 
        
        servere.data["id"] = id
        return make_response(render_template('EditServerPage.html', clientUser=user, server=servere.data, clientData=client), 200, headers)
