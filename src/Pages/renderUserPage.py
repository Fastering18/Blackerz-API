from flask_restful import Resource
from flask import jsonify, make_response, render_template, g, session, request, redirect, Markup
from requests_oauthlib import OAuth2Session
import time, json, requests, os, random, string, markdown
from threading import Timer, Thread
from src.util.database import mongoDB

from firebase import firebase
import pyrebase

configPyrebase = {
  "apiKey": "AIzaSyAQtuu-xm9Fvq1YNW9QNVlr07TduPFXEDI",
  "authDomain": "blackerz.firebaseapp.com",
  "databaseURL": "https://blackerz-default-rtdb.firebaseio.com",
  "storageBucket": "blackerz.appspot.com"
}

Fyrebase = pyrebase.initialize_app(configPyrebase)

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
storage = Fyrebase.storage()
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

def deleteCache(link):
    if not link in botCaches: return False
    del botCaches[link]
    return True

def putCache(link, isi):
    botCaches[link] = isi
    Timer(8.0, deleteCache, [link]).start()
    return True 

def updateBotData(id, result, tipe="botlist"):
    try:
        url = "https://discord.com/api/v8/users/" + str(id)
        r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
        response = r.json() 
        
        if response and "username" in response and "avatar" in response and "discriminator" in response and response["username"] and response["discriminator"]:
            mongoDB().uploadBot(id=id, data={
              "name": response["username"],
              "avatar": response["avatar"],
              "tag": response["username"] + "#" + response["discriminator"]
            })
        #if result["name"] != response["username"]:
            #result["name"] = response["username"]
            #result["tag"] = response["username"] + "#" + response["discriminator"]
            #firebaseDB.put(f'/Infrastructure/{tipe}/' + str(id), "name", response["username"])
            #firebaseDB.put(f'/Infrastructure/{tipe}/' + str(id), "tag", result["tag"])
            #if "avatar" in result and "avatar" in response:
                #if result["avatar"] != response["avatar"]:
                    #result["avatar"] = response["avatar"]
                    #firebaseDB.put(f'/Infrastructure/{tipe}/' + str(id), "avatar", response["avatar"])       
                #elif "avatar" in response and not "avatar" in result:
                    #result["avatar"] = response["avatar"]
                    #firebaseDB.put(f'/Infrastructure/{tipe}/' + str(id), "avatar", response["avatar"])
            #return response
    except Exception as kesalahan:
        print(kesalahan)         
  
class data():
    def __init__(self, dataName, id):
        if (dataName + str(id)) in botCaches:
            self.data = botCaches[dataName + str(id)]  
            return
          
        result = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
        if result != None:
            self.data = result
        else:
            self.data = None
        putCache(dataName + str(id), result)
            
error1 = {'error': "Bot not found", 'status': "Not success"}
        
class botPage(Resource):
  def get(self, id):
    if "http://" in request.url:
        return redirect(request.url.replace("http://", "https://", 1))
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    bot = mongoDB().get_bot(id=str(id))
    
    if bot != None:
        Thread(target=updateBotData, args=[id, bot]).start() 
        if "LongDescription" in bot:
            bot["LongDescription"] = Markup(markdown.markdown(bot["LongDescription"]))
        return make_response(render_template('botPage.html', botData=bot, botId=str(id), clientUser=user, jsonBotData=json.dumps(bot).replace("'", "\\'").replace('"', '\\"')), 200, headers)
    else:
        notFound = {
            'description': "Bot not found"
        }
        return make_response(render_template('404.html', notFound=notFound, clientUser=user, request=request), 404, headers)

class blackerzProfile(Resource):
  def get(self, filename):
    imageURL = storage.child(filename).get_url(token="3581d47e-3e11-433b-b6b3-007d5c6b2e43")
    exist = requests.get(imageURL).status_code
    if exist >= 400:
      imageURL = storage.child("Default/AssetNotFound.png").get_url(token="3581d47e-3e11-433b-b6b3-007d5c6b2e43")
    return make_response(render_template('Images.html', imageURL=imageURL, path=filename), 200, headers)
    #return redirect("https://blackerz.herokuapp.com/static/Images/"+filename)
