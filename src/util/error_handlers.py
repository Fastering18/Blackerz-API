from flask import jsonify, make_response, render_template, session, redirect, Markup, request, url_for
import time, os, random, string, datetime, json, requests
from requests_oauthlib import OAuth2Session

OAUTH2_CLIENT_ID = "798496088750292993"
OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
OAUTH2_REDIRECT_URI = 'https://blackerz.herokuapp.com/api/v1/discord/callback'
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
headers = {'Content-Type': 'text/html'}

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

  
  
def page_not_found(e):
  if request.url.startswith('http://'):
    return redirect(request.url.replace('http:', 'https:', 1), code=301)
  discord = make_session(token=session.get('oauth2_token'))
  user = discord.get(API_BASE_URL + '/users/@me').json()
  notFound = {
     "description": "The requested resource is not found, check your URL again or report to Discord Ghosteez#1000"
  }
  #print(request.headers.get("Cf-Ipcountry"))
  return make_response(render_template('404.html', notFound=notFound, clientUser=user), 404, headers)
