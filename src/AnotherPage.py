from flask_restful import Resource, reqparse
from flask import jsonify, make_response, render_template, g, session, request, redirect
from requests_oauthlib import OAuth2Session
import time, json, requests, os, random, string, datetime
from threading import Timer, Thread
import src.util.database as databaseManager


class publicBotSitemap(Resource):
    # PUBLIC bot_sitemap.xml 
    def get(self):
        botlist = mongoDB().getAllBots()
        bots = [{"name": "sus", "id": 1},{"name": "sos", "id": 2}]
        strr = """<?xml version="1.0" encoding="utf-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
           %s
        </urlset>
        """
        botstr = ""
        for v in botlist:
            botstr += f"""<url>
            <loc>https://blackerz.herokuapp.com/bots/{v['id']}</loc>
            <lastmod>2021-07-14</lastmod>
            <changefreq>daily</changefreq>
            <priority>1.0</priority>
            </url>
            """
        strr %= botstr
        return make_response(strr, 200, {'Content-Type': 'application/xml'})
