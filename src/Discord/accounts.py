from flask import Flask, request, jsonify, make_response
from flask_restful import Resource
from firebase import firebase
import requests, os

OAUTH2_CLIENT_ID = "798496088750292993"
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
BOTTOKEN = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

def getDataAkun(id):
  try:
    return requests.get(url = f"{API_BASE_URL}/v8/users/{id}", headers={'Authorization': 'Bot ' + BOTTOKEN}).json()
  except Exception as kesalahan:
    print(kesalahan)
    return {"error": "cannot GET account data"}

class getAccountData(Resource):
  def get(self, id):
    return make_response(jsonify(getDataAkun(id)))
