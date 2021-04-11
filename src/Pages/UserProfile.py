from flask_restful import Resource
from flask import jsonify, make_response, render_template, session, request, redirect
from requests_oauthlib import OAuth2Session
import time, json, requests, datetime, os, random, string
from threading import Timer, Thread
from src.util.database import mongoDB

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

def getUserBots(userid, tipe="botlist"):
    try:
        item = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/{tipe}.json?orderBy="owner/id"&equalTo="{userid}"').json()
        return item
    except Exception as kesalahan:
        print(kesalahan)
        return {}

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
            self.data["code"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "code", user["code"])
            self.data["username"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "username", user["username"])
            authV1 = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/AuthorizationV1", None)
            createdAt = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/CreatedAt", None)
            if authV1 == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "AuthorizationV1", generateAuthorizationV1())
            if createdAt == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "CreatedAt", datetime.datetime.now().isoformat())
        elif tipe == "allBot":
            result = firebaseDB.get('/Infrastructure/botlist', None)
            self.data = result

def updateUserData(id, tag, username, avatar, code, olduser):
    UserData = {
       #'id': id,
       'tag': tag,
       'username': username,
       'avatar': avatar,
       'code': code
    }
    if isinstance(olduser, dict): 
        if olduser.get("AuthorizationV1") == None: UserData["AuthorizationV1"] = generateAuthorizationV1()
        if olduser.get("CreatedAt") == None: UserData["CreatedAt"] = datetime.datetime.now().isoformat()
    mongoDB().uploadUser(id=id, data=UserData)
    #data("postUserStats", user=UserData)
    
class ProfileUsers(Resource):
  def get(self, id):
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http:', 'https:', 1), code=301)
    discord = make_session(token=session.get('oauth2_token'))
    userProfile = discord.get(API_BASE_URL + '/users/@me').json()
    
    useragent = request.headers.get('User-Agent')
    user = mongoDB().get_user(id=str(id))
    
    if user and "username" in user and "tag" in user:
        try:
            url = "https://discord.com/api/v8/users/" + str(id)
            r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
            responsenew = r.json() 
            if not responsenew or not "username" in responsenew: return
            oneTimeCode = generateRandomKey(8)
            userDataTarget = [
               str(id),
               responsenew["username"] + "#" + responsenew["discriminator"],
               responsenew["username"],
               responsenew["avatar"],
               oneTimeCode,
               user
            ]
            Thread(target=updateUserData, args=userDataTarget).start()
        except Exception as kesalahan:
            print(kesalahan)
    
    if userProfile and "username" in userProfile and "discriminator" in userProfile and (user and "username" in user and user["id"] != userProfile["id"]):      
        oneTimeCode = generateRandomKey(8)
        userData = [
           str(userProfile["id"]),
           userProfile["username"] + "#" + userProfile["discriminator"],
           userProfile["username"],
           userProfile["avatar"],
           oneTimeCode,
           userProfile 
        ] 
        Thread(target=updateUserData, args=userData).start()         
        
    if not user:
        notFound = {
            'description': "User not found"
        }
        return make_response(render_template('404.html', notFound=notFound, clientUser=userProfile), 404, headers)
    
    userData = user
    userData["userId"] = str(id)
    userData["botsowned"] = getUserBots(str(id))
    print(userData)
    if userProfile and "id" in userProfile:  
        if str(id) != userProfile["id"]:
            if userData.get("AuthorizationV1"): del userData["AuthorizationV1"]
    else:
        if userData.get("AuthorizationV1"): del userData["AuthorizationV1"]

    return make_response(render_template('profile.html', user=userData, client=userProfile), 200, headers)
