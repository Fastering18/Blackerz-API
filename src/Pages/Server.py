import os
import random
import string
from flask_restful import Resource
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time
import json
import requests
from threading import Timer, Thread

from firebase import firebase

OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
OAUTH2_REDIRECT_URI = 'https://blackerz.herokuapp.com/api/v1/discord/callback'
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
headers = {'Content-Type': 'text/html'}
ksoftHeaders = {'Authorization': 'Bearer de6bec5e78a2edf5990bd10f8876d7ecfc829a69'}

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
class data():
    def __init__(self, tipe, **Data):
        if tipe == "postUserStats":
            user = Data.get('user', None)
            self.data = {}
            self.data["tag"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "tag", user["tag"])
            self.data["avatar"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "avatar", user["avatar"])
            # self.data["code"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "code", user["code"])
            self.data["username"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "username", user["username"])
            authV1 = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/AuthorizationV1", None)
            if authV1 == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "AuthorizationV1", generateAuthorizationV1())
        elif tipe == "allServers":
            result = firebaseDB.get('/Infrastructure/serverlist', None)
            self.data = result
        elif tipe == "specificServer":
            serverID = Data.get('serverId', "")
            result = firebaseDB.get('/Infrastructure/serverlist/' + serverID, None)
            self.data = result
def updateUserData(id, tag, username, avatar, code):
    UserData = {
       'client_id': id,
       'tag': tag,
       'username': username,
       'avatar': avatar,
       'code': code
    }
    data("postUserStats", user=UserData)  
    
class allServersPage(Resource):
  def get(self):
    if "http://" in request.url:
        return redirect(request.url.replace("http://", "https://", 1))
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    serverDataList = data("allServers")
    useragent = request.headers.get('User-Agent')
    
    if "id" in user and "username" in user:      
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
    else:
        user = "null"
    return make_response(render_template('servers.html', user=user, servers=json.dumps(serverDataList.data), json=json, request=request), 200, headers)

class specificServerPage(Resource):
  def get(self, id):
    if "http://" in request.url:
        return redirect(request.url.replace("http://", "https://", 1))
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    serverData = data("specificServer", serverId=str(id))
    useragent = request.headers.get('User-Agent')
    
    if not "id" in user and not "username" in user:      
        user = "null"        
        
    if serverData.data != None:
        return make_response(render_template('specificServers.html', user=user, server=serverData.data, json=json, serverID=str(id), request=request), 200, headers)
    else:
        return make_response(render_template('404.html', user=user), 404, headers)
