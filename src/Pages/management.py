from flask_restful import Resource
from flask import jsonify, make_response, render_template, session, request, redirect, url_for
from requests_oauthlib import OAuth2Session
import time, random, string, datetime, json, requests, os
from threading import Timer, Thread
from firebase import firebase

from src.util.database import mongoDB, send_webhook

OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
BOTTOKEN = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
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
        elif tipe == "postBotUser":
            dataREQ = Data.get('bot', None)
            ownerData = Data.get('owner', None)
            botData = None
            botID = dataREQ['botId']
            
            oldbotdata = mongoDB().get_bot(id=str(botID))
            if oldbotdata:
                self.result = {'error': "Bot already exists!", 'status': "not sucess"}
                return
            
            try: 
                botData = requests.get(url = f"{API_BASE_URL}/v8/users/{botID}", headers={'Authorization': f"Bot {BOTTOKEN}"}).json()
            except Exception:
                print(Exception)
                self.result = {'error': "Failed to get bot data", 'status': "not sucess"}
                return
            
            if not "id" in botData:
                self.result = {'error': "Bot not found", 'status': "not sucess"}
                return
            
            if not botData.get("bot"):
                self.result = {'error': "user is not a bot", 'status': "not sucess"}
                return
            
            if not "prefix" in dataREQ:
                self.result = {'error': "prefix data was not set", 'status': "not sucess"}
                return
            
            if len(dataREQ["prefix"]) > 5:
                self.result = {'error': "prefix must below 5 length of characters", 'status': "not sucess"}
                return
                
            dataFinal = {
                'name': botData['username'],
                'owner': {
                    'id': ownerData['id'],
                    'name': ownerData['username'] + "#" + ownerData['discriminator']
                },
                'prefix': dataREQ["prefix"],
                'tag': botData['username'] + "#" + botData['discriminator'],
                'avatar': botData["avatar"],
                'verified': False,
                'upvotes': 0,
                'id': botID
                }
            botum, result = mongoDB().uploadBot(id=botID, data=dataFinal)
            print(result)
            
            if result["sucess"]:
                send_webhook("https://discord.com/api/webhooks/870668015065247784/qg27HSWbAE0cNKAwEGUD5OiwpI_awpCb9bv14_tVZID4dy8oUVGdnQusT_1oMHJrGsry", {"content": f"<@{ownerData['id']}> Added bot <@{botID}> **({dataFinal['tag']})**"})
                
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "name", botData['username'])
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "owner", {
                    #'id': ownerData['id'],
                    #'name': ownerData['username']
                #})
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "tag", botData['username'] + "#" + botData['discriminator'])
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "upvotes", 0)
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "prefix", dataREQ['prefix'])
            #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "verified", False)
            #if "avatar" in botData:
                #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "avatar", botData['avatar'])
            #if "inviteLink" in dataREQ:
                #firebaseDB.put('/Infrastructure/botlist/' + dataREQ['botId'], "inviteLink", dataREQ['inviteLink'])
        
            self.result = {'error': None, 'status': "sucess"}
                
class AddBotPagePublic(Resource):
    def get(self):
        user = getDiscordUser(session) 
        if user and "id" in user and "username" in user:
            Thread(target=updateUser, args=[user]).start() 
        else:
            return redirect(f"/api/v1/discord/login?code={generateRandomKey(8)}&host={request.url_root}")
        
        session["X_CSRF_TOKEN"] = generateRandomKey(58, "._")
        respen = kuki(make_response(render_template('addbotpublic.html', user=user, csrf=session["X_CSRF_TOKEN"], ), 200, headers))

        return respen
    
    def post(self):
        #if request.headers.get("X-Forwarded-For") != "180.246.248.238":
            #print(request.remote_addr)
            #return "This feature currently on maintenance,     CLIENT: " + str(request.headers.get("X-Forwarded-For")) + "      SESSION: " + str(session["X_CSRF_TOKEN"]), 404
        
        user = getDiscordUser(session)
        formData = request.form or request.get_json()
        if user and "id" in user and "username" in user:
            Thread(target=updateUser, args=[user]).start()
        else:
            return redirect(f"/api/v1/discord/login?code={generateRandomKey(8)}&host={request.url_root}")
        
        print(formData)
        isCsrfEqual = formData["cEeSeReF"] == session["X_CSRF_TOKEN"]
        session["X_CSRF_TOKEN"] = generateRandomKey(59, "._")
        
        result = None
        
        if isCsrfEqual:
            result = data("postBotUser", bot=formData, owner=user)
            if result.result['error'] == None:
                return redirect("/bots/" + formData['botId'], code=301)
            else:
                respen = kuki(make_response(render_template('addbotpublic.html', user=user, csrf=session["X_CSRF_TOKEN"], warns=result.result['error']), 400, headers))
                return respen
                #return make_response(jsonify(result.result), 400, headers)
        else:
            return make_response(render_template('Unauthorized.html', user=user), 401, headers)
        
        #return make_response(jsonify(formData), 200, headers)
        
