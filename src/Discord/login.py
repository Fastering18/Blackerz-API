import os
from flask import Flask, g, session, redirect, request, url_for, jsonify
from flask_restful import Resource, reqparse
from requests_oauthlib import OAuth2Session

OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
OAUTH2_REDIRECT_URI = 'https://blackerz-api.herokuapp.com/api/v1/discord/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


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
        

class login(Resource):
  def get(self):
    scope = request.args.get(
        'scope',
        'identify')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    print("URL NYA:  " + authorization_url)
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
     return redirect("https://blackerz-id.web.app/", 200, jsonify(user=user, guilds=guilds, connections=connections))   
