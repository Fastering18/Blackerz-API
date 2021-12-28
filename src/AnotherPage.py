from flask_restful import Resource, reqparse
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time, json, requests, os, random, string, datetime
from datetime import datetime
#from threading import Timer, Thread
from src.util.database import mongoDB

xmlstart = """<?xml version="1.0" encoding="utf-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
           %s
        </urlset>
        """

def xml_item_format(dt):
    return f"""<url>
            <loc>https://blackerz.herokuapp.com/bots/{dt['id']}</loc>
            <lastmod>{datetime.today().strftime('%Y-%m-%d')}</lastmod>
            <changefreq>daily</changefreq>
            <priority>1.0</priority>
            </url>
            """

class publicBotSitemap(Resource):
    # PUBLIC bot_sitemap.xml 
    def get(self):
        botlist, jmlh = mongoDB().getAllBots()
        
        botstr = ""
        for v in botlist:
            botstr += xml_item_format(v)
 
        return make_response(xmlstart % botstr, 200, {'Content-Type': 'application/xml'})

class publicServerSitemap(Resource):
    # PUBLIC bot_sitemap.xml 
    def get(self):
        serverlist, jmlh = mongoDB().getAllServers()
        
        serverstr = ""
        for v in serverlist:
            serverstr += xml_item_format(v)
 
        return make_response(xmlstart % serverstr, 200, {'Content-Type': 'application/xml'})
