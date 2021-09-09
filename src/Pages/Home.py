from flask_restful import Resource
from flask import jsonify, make_response, render_template, g, session, request, redirect, url_for
from requests_oauthlib import OAuth2Session
import time, os, random, string, datetime, json, requests
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
headers = {
    'Content-Type': 'text/html'
}
ksoftHeaders = {'Authorization': 'Bearer de6bec5e78a2edf5990bd10f8876d7ecfc829a69'}
botCaches = {}

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

def deleteCache(tipe="botsverified"):
  if not tipe in botCaches: return False
  del botCaches[tipe]
  return True

def putCache(tipe, isi):
    botCaches[tipe] = isi
    Timer(6000.0, deleteCache, [tipe]).start()
    return True

def sortBy(dic, tipe="upvotes"):
    daftr = [] #list(dic.values())
    for keyy in dic:
        vInside = dic[keyy]
        vInside["id"] = keyy
        daftr.append(vInside)
    daftr.sort(key=lambda ddata: ddata.get(tipe, 0), reverse=True)
    daftr.sort(key=lambda ddata: ddata.get("id"))
    return daftr

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
        #elif tipe == "allBot":
            #if "botsverified" in botCaches:
                #self.data = botCaches["botsverified"]
                #return 
            #try:
                #result = requests.get('https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy=%22verified%22&equalTo=true').json() 
                #self.data = sortBy(result)
                #putCache("botsverified", self.data)
            #except Exception as kesalahan:
                #print(kesalahan)
                #try:
                    #result = firebaseDB.get('/Infrastructure/botlist', None)
                    #self.data = sortBy(result)
                #except Exception as kesalahan2:
                    #print(kesalahan2)
                    #self.data = "Internal error, this is not your error, please report this issues to github."
        elif tipe == "querySearch":
            kueri = Data.get('kueri', "bot")
            self.filter = "verified"
            if kueri + "_querysearch" in botCaches:
                self.result = botCaches[kueri + "_querysearch"]
                return 
            try:
                self.result = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy="{self.filter}"&equalTo=true').json()
                if kueri:
                    listres = [] 
                    for kunci in self.result:
                        if self.result[kunci]["name"].lower().startswith(kueri.lower()) or (kueri.lower() in self.result[kunci]["name"].lower()):
                            self.result[kunci]["id"] = kunci
                            listres.append(self.result[kunci])
                    self.result = listres
                putCache(kueri + "_querysearch", self.result)
            except Exception as kesalahan:
                print(kesalahan)
                self.result = data("allBot").data
            
def updateUserData(id, tag, username, avatar, code, olduser=None):
    UserData = {
       #'client_id': id,
       'tag': tag,
       'username': username,
       'avatar': avatar,
       'code': code
    }
    if olduser == None: olduser = mongoDB().get_user(id=id)
    if isinstance(olduser, dict): 
        if olduser.get("AuthorizationV1") == None: UserData["AuthorizationV1"] = generateAuthorizationV1()
        if olduser.get("CreatedAt") == None: UserData["CreatedAt"] = datetime.datetime.now().isoformat()
    mongoDB().uploadUser(id=id, data=UserData)
    #data("postUserStats", user=UserData)     
    
class homePage(Resource):
  def get(self):
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http:', 'https:', 1), code=301)
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    botDataList, jumlah = mongoDB().getAllBots() or []
    
    if user and "id" in user and "username" in user:      
        oneTimeCode = generateRandomKey(8)
        userData = [
           str(user["id"]),
           user["username"] + "#" + user["discriminator"],
           user["username"],
           user["avatar"],
           oneTimeCode
        ]
        Thread(target=updateUserData, args=userData).start() 
    else:
        user = "null"
    
    print(botDataList)
    
    respen = make_response(render_template('home.html', user=user, bots=botDataList), 200, headers)
    respen.set_cookie('same-site-cookie', '3pcookie', samesite='Lax');
    respen.set_cookie('cross-site-cookie', '3pcookie-legacy', samesite='Lax', secure=True);
    return respen

class BotSearchPage(Resource):
    def get(self):
        kueri = request.values.get("q") or request.values.get("query") or request.values.get("kueri")
        if kueri == None:
            return redirect(url_for('.homepage'), code=301)
        if request.url.startswith('http://'):
            return redirect(request.url.replace('http:', 'https:', 1), code=301)
        
        discord = make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        botsdata, jmlh = mongoDB().botQuerySearch(kueri=kueri) or []
        
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
        else:
            user = "null"
            
        respen = make_response(render_template('home.html', user=user, bots=botsdata, kueri=kueri), 200, headers)
        respen.set_cookie('same-site-cookie', '3pcookie', samesite='Lax');
        respen.set_cookie('cross-site-cookie', '3pcookie-legacy', samesite='Lax', secure=True);
        return respen  
        
