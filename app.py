from flask import Flask
from flask_restful import Api

from src.searchbot import resouce
from src.allbot import resource2
from src.submitbot import resource3
from src.editBotData import editData
from src.Templates.renderUserPage as renderUserPage

import src.Discord.login as discordLoginSource

import src.Servers.searchserver as searchServer
import src.Servers.allservers as allServers
import src.Servers.submitserver as submitServer

import src.Voting as VotingManager

OAUTH2_CLIENT_SECRET = "aGcXd7_izART3A5zT-V6yhPqu-Fmr3-M"

app = Flask(__name__)
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
api = Api(app)

# Discord bots resource
api.add_resource(resouce, "/api/v1/bots/<int:id>")
api.add_resource(resource2, "/api/v1/bots/all")
api.add_resource(resource3, "/api/v1/bots/submit/<int:id>")
api.add_resource(editData, "/api/v1/bots/<int:id>/edit")

# Discord login resource
api.add_resource(discordLoginSource.login, "/api/v1/discord/login")
api.add_resource(discordLoginSource.callback, "/api/v1/discord/callback")
api.add_resource(discordLoginSource.me, "/api/v1/discord/me")
api.add_resource(discordLoginSource.checkUser, "/api/v1/discord/check")

# Discord servers resource
api.add_resource(allServers.findAllServer, "/api/v1/servers/all")
api.add_resource(searchServer.findServer, "/api/v1/servers/<int:id>")
api.add_resource(submitServer.postServer, "/api/v1/servers/submit/<int:id>")

# Votes bots and servers resource
api.add_resource(VotingManager.voteBot, "/api/v1/bots/<int:id>/vote")

# Render pages
api.add_resource(renderUserPage.botPage, "/api/v1/bots/<int:id>")

if __name__ == "__main__":
  app.run()
