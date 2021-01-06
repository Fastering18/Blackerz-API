from flask import Flask
from flask_restful import Api

from src.searchbot import resouce
from src.allbot import resource2

app = Flask(__name__)
api = Api(app)

bots = {
    717660707650273280: {
        "name": "Goblox",
        "id": "717660707650273280",
        "tag": "Goblox#2087"
    },
    790473894443352074: {
        "name": "Nub Yup",
        "id": "790473894443352074",
        "tag": "NubYup bot#9393"
    }
}

api.add_resource(resouce, "/api/v1/bots/<int:id>")
api.add_resource(resource2, "/api/v1/bots/all")

if __name__ == "__main__":
  app.run()
