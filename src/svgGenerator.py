from flask_restful import Resource
from flask import jsonify, make_response, request, redirect, render_template, Markup
import time, json, requests, string
from threading import Timer
#from cairosvg import svg2png
from src.util.database import notifyChanges, mongoDB

from firebase import firebase

svgheaders = {'Content-Type': 'image/svg+xml'}
pngheaders = {'Content-Type': 'image/png'}
htmlheaders = {'Content-Type': 'text/html'}
imagecaches = {
   "bots": {
      "717660707650273280": {}
   }
}

def getServerCountBotFromID(botID):
  try:
    servercount = mongoDB().get_bot(id=str(botID)) #requests.get(f"https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist/{botID}/serverCount.json").json()
    if not servercount or (servercount and not "serverCount" in servercount): return None
    return servercount["serverCount"]
  except:
    return None

def deleteCache(itemID, dataName, type="bots"):
  del imagecaches[type][itemID]
  return True
  
def putCache(itemID, dataName, value, type="bots"):
  itemID = str(itemID)
  if not itemID in imagecaches[type]: 
    imagecaches[type][itemID] = {} # [dataName]: value
    return putCache(itemID, dataName, value, type="bots") # recursion cause idk
  elif not dataName in imagecaches[type][itemID]:
    imagecaches[type][itemID][dataName] = value
  elif value != imagecaches[type][itemID][dataName]:
    return False
  Timer(60.0, deleteCache, [itemID, dataName, type]).start()
  return True
  
class getServerCountBot(Resource):
  def get(self, id, mime):
    if not mime in [".svg", "./png"]: return make_response(render_template('404.html', notFound="Invalid mime type"), 404, htmlheaders)
    id = str(id)
    if id in imagecaches["bots"] and mime == ".svg" and "servercount" in imagecaches["bots"][id]:
      return make_response(Markup(imagecaches["bots"][id]["servercount"]), 200, svgheaders)
    if id in imagecaches["bots"] and mime == ".png" and "servercountPNG" in imagecaches["bots"][id]:
      return make_response(imagecaches["bots"][id]["servercountPNG"], 200, pngheaders)
   
    servercount = getServerCountBotFromID(id)
    if servercount == None: return make_response(jsonify({"error": True, "message": "No data found"}), 404, {'Content-Type': 'application/json'})
    
    gambarJadi = f'''<?xml version="1.0" encoding="UTF-8"?>
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
    if mime == ".svg":
      putCache(id, "servercount", gambarJadi, type="bots")
      return make_response(Markup(gambarJadi), 200, svgheaders)
    elif mime == ".png":
      gambarJadi = svg2png(bytestring=gambarJadi)
      putCache(id, "servercountPNG", gambarJadi, type="bots")
      return make_response(gambarJadi, 200, pngheaders) 
