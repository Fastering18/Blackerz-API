from flask import Flask, make_response, request, send_file
from flask_restful import Api, Resource
from flask_compress import Compress
from flask_hcaptcha import hCaptcha
from flask_caching import Cache

import src.Pages.Home as Home
import src.Pages.Server as Servers
import src.Pages.UserProfile as Profile
import src.Pages.renderUserPage as renderUserPage
import src.Pages.VotingPage as votingPage
import src.Pages.editDataPage as editPage
import src.Pages.management as mainManagement

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

# Static pages resource
api.add_resource(Home.homePage, "/")
api.add_resource(Home.BotSearchPage, "/search")
api.add_resource(Servers.allServersPage, "/servers")
api.add_resource(Profile.ProfileUsers, "/user/<int:id>")
api.add_resource(renderUserPage.blackerzProfile, "/Assets/<path:filename>")

# Discord bots resource
api.add_resource(searchBots.getBotFromID, "/api/v1/bots/<int:id>")
api.add_resource(searchBots.searchBotQuery, "/api/v1/bots/search")
api.add_resource(resource2, "/api/v1/bots/all")
api.add_resource(resource3, "/api/v1/bots/submit/<int:id>")
api.add_resource(editBotData.editData, "/api/v1/bots/<int:id>/edit")
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
api.add_resource(submitServer.postServer, "/api/v1/servers/submit/<int:id>")

# Votes bots and servers resource
api.add_resource(VotingManager.voteBot, "/api/v1/bots/<int:id>/vote")
api.add_resource(VotingManager.publicVoteApiBot, "/api/v1/bots/<int:id>/votes")
api.add_resource(VotingManager.voteServer, "/api/v1/servers/<int:id>/vote")
api.add_resource(VotingManager.publicVoteApiServer, "/api/v1/servers/<int:id>/votes")

# Render pages
api.add_resource(renderUserPage.botPage, "/bots/<int:id>")
api.add_resource(votingPage.BotVotePage, "/bots/<int:id>/vote")
api.add_resource(editPage.EditBotPage, "/bots/<int:id>/edit")
api.add_resource(Servers.specificServerPage, "/servers/<int:id>")
api.add_resource(votingPage.ServerVotePage, "/servers/<int:id>/vote")
api.add_resource(editPage.EditServerPage, "/servers/<int:id>/edit")

# Utility & Management
api.add_resource(mainManagement.AddBotPagePublic, "/add/bot")

# Widgets
api.add_resource(svggenerator.getServerCountBot, "/api/v1/bots/<int:id>/widgets/servers<string:mime>")

# FILE
class dptFile(Resource):
  def get(self):
    return make_response(
"""user-agent: *
allow: /""", 200, {'Content-Type': 'text/plain'})

class dptFile2(Resource):
  def get(self):
    return make_response(send_file("./static/sitemap.xml"), 200)
  
api.add_resource(dptFile, "/robots.txt")
api.add_resource(dptFile2, "/sitemap.xml")

if __name__ == "__main__":
  app.run()
