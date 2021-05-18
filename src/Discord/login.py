import os, random, string, requests, datetime
from flask import Flask, session, redirect, request, url_for, jsonify, make_response
from flask_restful import Resource, reqparse
from requests_oauthlib import OAuth2Session
from firebase import firebase
from src.util.database import mongoDB
from bson.json_util import dumps

OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
OAUTH2_REDIRECT_URI = 'https://blackerz.herokuapp.com/api/v1/discord/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
LOGOUT_BASE_URL = API_BASE_URL + '/oauth2/revoke'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

errorInvalidHeaders1 = {'error': "Invalid headers data request, read our documentation for details", 'status': "Not success"}
errorInvalidUser = {'error': "User not found", 'status': "Not success"}
UnauthorizedAccess1 = {'error': "Unauthoried access, please enter correct code", 'status': "Not success"}

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

def token_updater(token):
    session['oauth2_token'] = token

def generateRandomKey(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str
def generateAuthorizationV1():
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(random.randint(21, 24)))
    return result_str
    
class data():
    def __init__(self, user):
        self.data = {}
        self.data["tag"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "tag", user["tag"])
        self.data["avatar"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "avatar", user["avatar"])
        self.data["code"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "code", user["code"])
        self.data["username"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "username", user["username"])
        authV1 = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/AuthorizationV1", None)
        createdAt = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/CreatedAt", None)
        if authV1 == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "AuthorizationV1", generateAuthorizationV1())
        if createdAt == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "CreatedAt", datetime.datetime.now().isoformat())
        olduser = mongoDB().get_user(id=user["client_id"])
        if isinstance(olduser, dict): 
            if not olduser.get("AuthorizationV1"): user["AuthorizationV1"] = generateAuthorizationV1()
            if not olduser.get("CreatedAt"): user["CreatedAt"] = datetime.datetime.now().isoformat()
        mongoDB().uploadUser(id=user["client_id"], data=user)
        #timeStamp = time.time()

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
        

class login(Resource):
  def get(self):
    if request.values.get('code'):
         code = request.values['code']
    scope = request.args.get(
        'scope',
        'identify')
    discord = make_session(scope=scope.split(' '), redirectURL=request.url_root + "api/v1/discord/callback")
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    host = ""
    if request.values.get('host'):
         host = "&host=" + request.values['host']
    response = redirect(authorization_url)
    return response
        
class callback(Resource):
  def get(self):
     print(request.url)
     if request.values.get('error'):
         host = "https://blackerz.web.app/" 
         if request.cookies.get('dariLink'):
             host = request.cookies['dariLink']
             if (host == "blackerz.herokuapp.com"): 
                 host = "https://" + host
         return redirect(host)
     discord = make_session(state=session.get('oauth2_state'), redirectURL=request.url_root + "api/v1/discord/callback")
     token = discord.fetch_token(
         TOKEN_URL,
         client_secret=OAUTH2_CLIENT_SECRET,
         authorization_response=request.url)
     session['oauth2_token'] = token
        
     return redirect(url_for('.me')) 
  
class me(Resource):
  def get(self):
     discord = make_session(token=session.get('oauth2_token'), redirectURL=request.url_root + "api/v1/discord/callback")
     user = discord.get(API_BASE_URL + '/users/@me').json()
     # return jsonify(user=user, guilds=guilds, connections=connections)
     oneTimeCode = generateRandomKey(8)
     userID = user["id"]
     data({
      'client_id': str(userID),
      'tag': user.get("username") + "#" + user.get("discriminator"),
      'username': user.get("username"),
      'avatar': user.get("avatar"),
      'code': oneTimeCode
     })
    
     if request.values.get('fromOrigin'):
        return make_response(jsonify(user), 200)
        
     host = "https://blackerz.web.app/" 
     params = "?code=" + oneTimeCode + "&client_id=" + userID
     if request.cookies.get('dariLink'):
        host = request.cookies['dariLink']
        if (host == "blackerz.herokuapp.com" or host == "blackerz.tk"): 
            params = ""
            host = "https://" + host
     print(host)  
     return redirect(host + params)
     #return make_response(jsonify(user), 200)

class logOut(Resource):
  def get(self):
      print(session.keys())
      session.clear()
      host = url_for('.homepage')
      if request.values.get('callback'):
          host = request.values.get('callback')
      return redirect(host)
        
class checkUser(Resource):
    def get(self):
        authv1 = request.headers.get('Authorization')
        if authv1:
            user = mongoDB().get_user(AuthorizationV1=authv1)
            return make_response(dumps(user) if user != None else jsonify({"error": "User not found", "success": False}), 200 if user != None else 401)
        code = request.headers.get('code')
        clientId = request.headers.get('clientId')
        if clientId == None or code == None:
            return make_response(jsonify(errorInvalidHeaders1), 400)
        result = firebaseDB.get('/Infrastructure/WebUsers/'+ clientId, None)
        if result == None:
            return make_response(jsonify(errorInvalidUser), 404)
        if not "code" in result or not result["code"] == code:
            return make_response(jsonify(UnauthorizedAccess1), 401)
        respon = {'clientId': clientId, 'tag': result["tag"], 'username': result["username"]}    
        if 'AuthorizationV1' in result : respon["AuthorizationV1"] = result["AuthorizationV1"];
        if 'avatar' in result : respon['avatar'] = result["avatar"];
            
        return make_response(jsonify(respon), 200)
