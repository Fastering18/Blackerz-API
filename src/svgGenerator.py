from flask_restful import Resource
from flask import jsonify, make_response, request, redirect, Markup
import time, json, requests, string
from threading import Timer

from firebase import firebase

headers = {
    'Content-Type': 'image/svg+xml'
}
svgcaches = {
   "bots": {
      "717660707650273280": {}
   }
}

def getServerCountBotFromID(botID):
  try:
    servercount = requests.get(f"https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist/{botID}/serverCount.json").json()
    return servercount
  except:
    return None

def deleteCache(itemID, dataName, type="bots"):
  del svgcaches[type][itemID][dataName]
  return True
  
def putCache(itemID, dataName, value, type="bots"):
  itemID = str(itemID)
  if not itemID in svgcaches[type]: 
    svgcaches[type][itemID] = {} # [dataName]: value
    return putCache(itemID, dataName, value, type="bots") # recursion cause idk
  elif not dataName in svgcaches[type][itemID]:
    svgcaches[type][itemID][dataName] = value
  elif value != svgcaches[type][itemID][dataName]:
    return False
  Timer(60.0, deleteCache, (itemID, dataName, type)).start()
  print(svgcaches)
  return True
  
class getServerCountBot(Resource):
  def get(self, id):
    id = str(id)
    if id in svgcaches["bots"] and "servercount" in svgcaches["bots"][id]:
      return make_response(Markup(svgcaches["bots"][id]["servercount"]), 200, headers)
    
    servercount = getServerCountBotFromID(id)
    if servercount == None: return make_response(jsonify({"error": True, "message": "Bot not found"}), 404)
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
    <linearGradient id="a" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"></stop>
        <stop offset="1" stop-opacity=".1"></stop></linearGradient>
    <rect rx="3" width="120" height="20" fill="#555"></rect>
    <rect rx="3" x="50" width="70" height="20" fill="#4c1"></rect>
    <rect rx="3" width="120" height="20" fill="url(#a)"></rect>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="23" y="15" fill="#010101" fill-opacity=".3">Servers</text>
        <text x="23" y="14">Servers</text>
        <text x="85" y="15" fill="#010101" fill-opacity=".3">{servercount}</text>
        <text x="85" y="14">{servercount}</text>
    </g>
    </svg>'''
    putCache(id, "servercount", svg, type="bots")
    return make_response(Markup(svg), 200, headers)
    
