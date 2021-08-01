from flask import Flask, make_response, request, send_file
from flask_restful import Api, Resource
from flask_compress import Compress
from flask_hcaptcha import hCaptcha
from flask_caching import Cache
import sentry_sdk, requests
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration
from src.util.database import dbInfrastructure, firebaseDB, dbAdmins 

import src.Pages.Home as Home
import src.Pages.Server as Servers
import src.Pages.UserProfile as Profile
import src.Pages.renderUserPage as renderUserPage
import src.Pages.VotingPage as votingPage
import src.Pages.editDataPage as editPage
import src.Pages.management as mainManagement

import src.util.error_handlers as error_handlers

import src.searchbot as searchBots
from src.allbot import resource2
from src.submitbot import resource3
import src.editBotData as editBotData

import src.Discord.login as discordLoginSource
import src.Discord.accounts as discordAccountSource

import src.Servers.searchserver as searchServer
import src.Servers.allservers as allServers
import src.Servers.submitserver as submitServer

import src.Voting as VotingManager
import src.svgGenerator as svggenerator
import src.AnotherPage as AnotherPage

OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"
hcaptcha = hCaptcha()

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
app.config['UPLOAD_FOLDER'] = "Images"
app.config['HCAPTCHA_SITE_KEY'] = "552252c3-1e0d-4fa8-837f-045a91f369ec"
app.config['RECAPTCHA_SECRET_KEY'] = "0x1a92Fc4CD3367d965aa5ffb3B5107710f5a7e0D6"
app.config['CACHE_TYPE'] = "SimpleCache"
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
Compress(app)
hcaptcha.init_app(app)
cache = Cache(app)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
    
app.register_error_handler(404, error_handlers.page_not_found)  
        
sentry_sdk.init(
    dsn="https://9e4fd61150b74cdaa14638fbb06e2df7@o562461.ingest.sentry.io/5701013",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)  

#users = firebaseDB.get("/Infrastructure/WebUsers", None)
#print(users)
#for userid in users:
    #users[userid]["id"] = userid
    #dbInfrastructure.users.update_one({"id": userid}, { "$set": users[userid] }, upsert=True)

# Static pages resource
api.add_resource(Home.homePage, "/")
api.add_resource(Home.BotSearchPage, "/search")
api.add_resource(Servers.searchServerQuery, "/servers/search")
api.add_resource(Servers.allServersPage, "/servers")
api.add_resource(Profile.ProfileUsers, "/user/<int:id>")
api.add_resource(renderUserPage.blackerzProfile, "/Assets/<path:filename>")

# Discord bots resource
api.add_resource(searchBots.getBotFromID, "/api/v1/bots/<int:id>")
api.add_resource(searchBots.searchBotQuery, "/api/v1/bots/search")
api.add_resource(searchBots.autocorrectsearch, "/api/v1/bots/autocorrect")
api.add_resource(resource2, "/api/v1/bots/all")
api.add_resource(resource3, "/api/v1/bots/submit/<int:id>")
api.add_resource(editBotData.editData, "/api/v1/bots/<int:id>/edit")
api.add_resource(editBotData.VerifyBot, "/api/v1/bots/<int:id>/_verify")
api.add_resource(searchBots.deleteBotFromID, "/api/v1/bots/<int:id>/delete")
api.add_resource(editBotData.ServerCountManager, "/api/v1/bots/<int:id>/edit/servercount")

# Discord login resource
api.add_resource(discordLoginSource.login, "/api/v1/discord/login")
api.add_resource(discordLoginSource.callback, "/api/v1/discord/callback")
api.add_resource(discordLoginSource.me, "/api/v1/discord/me")
api.add_resource(discordLoginSource.checkUser, "/api/v1/discord/check")
api.add_resource(discordLoginSource.logOut, "/api/v1/discord/logout")
api.add_resource(discordAccountSource.getAccountData, "/api/v1/discord/account/<int:id>")

# Discord servers resource
api.add_resource(allServers.findAllServer, "/api/v1/servers/all")
api.add_resource(searchServer.findServer, "/api/v1/servers/<int:id>")
api.add_resource(searchServer.autocorrectServer, "/api/v1/servers/autocorrect")
api.add_resource(submitServer.postServer, "/api/v1/servers/submit/<int:id>")
api.add_resource(submitServer.editServer, "/api/v1/servers/<int:id>/edit")

# Votes bots and servers resource
api.add_resource(VotingManager.voteBot, "/api/v1/bots/<int:id>/vote")
api.add_resource(VotingManager.voteBotAdmin, "/api/v1/bots/<int:id>/_adminvote") #admin only
api.add_resource(VotingManager.publicVoteApiBot, "/api/v1/bots/<int:id>/votes")
api.add_resource(VotingManager.voteServer, "/api/v1/servers/<int:id>/vote")
api.add_resource(VotingManager.publicVoteApiServer, "/api/v1/servers/<int:id>/votes")

# Render pages
api.add_resource(renderUserPage.botPage, "/bots/<int:id>")
api.add_resource(votingPage.BotVotePage, "/bots/<int:id>/vote")
api.add_resource(editPage.EditBotPage, "/bots/<int:id>/edit")
api.add_resource(editPage.WebhookBotPage, "/bots/<int:id>/webhooks")
api.add_resource(Servers.specificServerPage, "/servers/<int:id>")
api.add_resource(votingPage.ServerVotePage, "/servers/<int:id>/vote")
api.add_resource(editPage.EditServerPage, "/servers/<int:id>/edit")

# Utility & Management
api.add_resource(mainManagement.AddBotPagePublic, "/add/bot")

# Widgets
api.add_resource(svggenerator.getServerCountBot, "/api/v1/bots/<int:id>/widgets/servers<string:mime>")

# sitemaps & others
api.add_resource(AnotherPage.publicBotSitemap, "/bots_sitemap.xml")


# FILE
class dptFile(Resource):
  def get(self):
    return make_response(
"""user-agent: *
allow: /
Sitemap: https://blackerz.herokuapp.com/static/sitemapindex.xml""", 200, {'Content-Type': 'text/plain'})

class dptFile2(Resource):
  def get(self):
    return make_response(send_file("./static/sitemap.xml"), 200)

class dptFile3(Resource):
  def get(self):
    res = requests.get("https://arc.io/arc-sw.js")
    return make_response(res.content, res.status_code, {'Content-Type': 'text/javascript'}) #make_response(send_file("./static/arc-sw.js"), 200)

class dptFile4(Resource):
  def get(self):
    return make_response(send_file("./static/Images/favicon.ico"), 200)

class dptFile5(Resource):
  def get(self):
    return make_response(send_file("./static/opensearch.xml"), 200)

class dptFile6(Resource):
  def get(self):
    res = requests.get("https://disqusads.com/ads.txt")
    return make_response(res.content, res.status_code, {'Content-Type': 'text/plain'})
  
api.add_resource(dptFile, "/robots.txt")
api.add_resource(dptFile2, "/sitemap.xml")
api.add_resource(dptFile3, "/arc-sw.js")
api.add_resource(dptFile4, "/favicon.ico")
api.add_resource(dptFile5, "/opensearch.xml")
api.add_resource(dptFile6, "/ads.txt")

if __name__ == "__main__":
  app.run()
