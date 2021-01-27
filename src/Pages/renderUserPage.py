from flask_restful import Resource
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time
import json
import requests
import os
import random
import string

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
    print(result_str)
            
class data():
    def __init__(self, dataName, id):
        result = firebaseDB.get('/Infrastructure/botlist/' + str(id), None)
        if result != None:       
            url = "https://discord.com/api/v8/users/" + str(id)
            r = requests.get(url = url, headers={'Authorization': 'Bot ' + botToken}) 
            response = r.json() 

            if result["name"] != response["username"]:
                result["name"] = response["username"]
                firebaseDB.put('/Infrastructure/botlist/' + str(id), "name", response["username"])
            if "avatar" in result and "avatar" in response:
                if result["avatar"] != response["avatar"]:
                    result["avatar"] = response["avatar"]
                    firebaseDB.put('/Infrastructure/botlist/' + str(id), "avatar", response["avatar"])       
            elif "avatar" in response and not "avatar" in result:
                result["avatar"] = response["avatar"]
                firebaseDB.put('/Infrastructure/botlist/' + str(id), "avatar", response["avatar"])
            self.data = result
            self.timeStamp = time.time()
        else:
            self.data = None
            
error1 = {'error': "Bot not found", 'status': "Not success"}
        
class botPage(Resource):
  def get(self, id):
    if request.url_root == "http://blackerz.herokuapp.com/":
        return redirect("https://blackerz.herokuapp.com/bots/" + str(id))
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    botum = data("getbot", id)
    bot = botum.data
    
    if bot != None:
        botName = bot["name"]
        short_description = ""
        if "ShortDescription" in bot:
            short_description = bot["ShortDescription"]
        return make_response(render_template('botPage.html', botData=bot, botId=str(id), clientUser=user), 200, headers)
    else:
        notFound = {
            'description': "Bot not found"
        }
        return make_response(render_template('404.html', notFound=notFound, clientUser=user), 404, headers)

class blackerzProfile(Resource):
  def get(self, filename):
    return redirect("https://blackerz.herokuapp.com/static/Images/"+filename)
