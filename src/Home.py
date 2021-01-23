from flask_restful import Resource
from flask import jsonify, make_response, render_template
import time
import requests
from threading import Timer

from firebase import firebase

botToken = "Nzk4NDk2MDg4NzUwMjkyOTkz.X_13bg.sBzU_MurYpOqy_Px5WvW2GF7VT8"
firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
headers = {'Content-Type': 'text/html'}
                    
class homePage(Resource):
  def get(self):
    return make_response(render_template('home.html'), 200, headers)
