from flask_restful import Resource
from flask import jsonify

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

class resouce(Resource):
  def get(self, id):
    if id in bots:
        return jsonify(bots[id])
    else:
        return "<h1>404 Bot tidak ditemukan untuk id: {}".format(id), 404
