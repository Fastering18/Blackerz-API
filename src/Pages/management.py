from flask_restful import Resource
from flask import jsonify, make_response, render_template, session, request, redirect, url_for
from requests_oauthlib import OAuth2Session
import time, random, string, datetime, json, requests, os
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
headers = {
    'Content-Type': 'text/html'
}

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

def generateRandomKey(length, anotherletter=""):
    letters_and_digits = string.ascii_letters + string.digits + anotherletter
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def generateAuthorizationV1():
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(random.randint(21, 24)))
    return result_str
  
def getDiscordUser(sesi):
    discord = make_session(token=sesi.get('oauth2_token'))
    return discord.get(API_BASE_URL + '/users/@me').json()

def updateUser(datauser):
    oneTimeCode = generateRandomKey(8)
    userData = {
        'client_id': str(datauser["id"]),
        'tag': datauser["username"] + "#" + datauser["discriminator"],
        'username': datauser["username"],
        'avatar': datauser["avatar"],
        'code': oneTimeCode
    }
    data("postUserStats", user=userData)
    
def kuki(respen):
    respen.set_cookie('same-site-cookie', '3pcookie', samesite='Lax');
    respen.set_cookie('cross-site-cookie', '3pcookie-legacy', samesite='Lax', secure=True);
    return respen

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
            createdAt = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/CreatedAt", None)
            if authV1 == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "AuthorizationV1", generateAuthorizationV1())
            if createdAt == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "CreatedAt", datetime.datetime.now().isoformat())                
                
class AddBotPagePublic(Resource):
    def get(self):
        user = getDiscordUser(session) 
        if user and "id" in user and "username" in user:
            Thread(target=updateUser, args=[user]).start() 
        else:
            return redirect(f"/api/v1/discord/login?code={generateRandomKey(8)}&host={request.host}")
        
        session["X_CSRF_TOKEN"] = generateRandomKey(58, "._")
        respen = kuki(make_response(render_template('addbotpublic.html', user=user, csrf=session["X_CSRF_TOKEN"]), 200, headers))

        return respen
    
    def post(self):
        user = getDiscordUser(session)
        jsonData = request.get_json()
        if user and "id" in user and "username" in user:
            Thread(target=updateUser, args=[user]).start()
        
        print(jsonData)
        return make_response(jsonify(user), 200, headers))
        
