from flask_restful import Resource, reqparse
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time, json, requests, os, random, string
from threading import Timer

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
  
class EditBotPage(Resource):
    def get(self, id):
        if "http://" in request.url:
            return redirect(request.url.replace("http://", "https://", 1))
        discord = make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        
        if not "id" in user:
            return make_response(render_template('Unauthorized.html', user=user), 401, headers)
        isOwner = verifyOwner(user.id, str(id))
        if isOwner["success"] == False:
            return make_response(render_template('Unauthorized.html', user=user), 401, headers) 
          
        return make_response(jsonify({"success": True}))
        
