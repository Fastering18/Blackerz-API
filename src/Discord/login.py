import os
import random
import string
from flask import Flask, g, session, redirect, request, url_for, jsonify, make_response
from flask_restful import Resource, reqparse
from requests_oauthlib import OAuth2Session
from firebase import firebase

OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
OAUTH2_REDIRECT_URI = 'https://blackerz-api.herokuapp.com/api/v1/discord/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

loginUsersEntry = [

]
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

class data():
    def __init__(self, user):        
        result = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "tag", user["tag"])
        result = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "avatar", user["avatar"])
        result = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "code", user["code"])
        self.data = result
        #timeStamp = time.time()

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
        

class login(Resource):
  def get(self):
    if request.values.get('code'):
         code = request.values['code']
         loginUsersEntry.append(code)
    scope = request.args.get(
        'scope',
        'identify')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)
        
class callback(Resource):
  def get(self):
     if request.values.get('error'):
         return request.values['error']
     discord = make_session(state=session.get('oauth2_state'))
     token = discord.fetch_token(
         TOKEN_URL,
         client_secret=OAUTH2_CLIENT_SECRET,
         authorization_response=request.url)
     session['oauth2_token'] = token
        
     return redirect(url_for('.me')) 
  
class me(Resource):
  def get(self):
     discord = make_session(token=session.get('oauth2_token'))
     user = discord.get(API_BASE_URL + '/users/@me').json()
     guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
     connections = discord.get(API_BASE_URL + '/users/@me/connections').json()
     # return jsonify(user=user, guilds=guilds, connections=connections)
     oneTimeCode = generateRandomKey(8)
     userID = user["id"]
     data({
      'client_id': userID,
      'tag': user["username"] + "#" + user["discriminator"],
      'username': user["username"]
      'avatar': user["avatar"],
      'code': oneTimeCode
     })
     # Response = make_response(jsonify(user=user), 200)
     return redirect("https://blackerz-id.web.app?code=" + oneTimeCode + "&client_id=" + userID)     

class checkUser(Resource):
    def get(self):
        code = request.headers.get('code')
        clientId = request.headers.get('clientId')
        if clientId == None or code == None:
            return make_response(jsonify(errorInvalidHeaders1), 400)
        result = firebaseDB.get('/Infrastructure/WebUsers/'+ clientId, None)
        if result == None:
            return make_response(jsonify(errorInvalidUser), 404)
        print(result)
        if not "code" in result or not result["code"] == code:
            return make_response(jsonify(UnauthorizedAccess1), 401)
        respon = {'clientId': clientId, 'avatar': result["avatar"], 'tag': result["tag"], 'username': result["username"]}
        return make_response(jsonify(respon), 200)
