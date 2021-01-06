from flask import Flask
from flask_restful import Api

from src.searchbot import resouce
from src.allbot import resource2

app = Flask(__name__)
api = Api(app)

api.add_resource(resouce, "/api/v1/bots/<int:id>")
api.add_resource(resource2, "/api/v1/bots/all")

if __name__ == "__main__":
  app.run()
