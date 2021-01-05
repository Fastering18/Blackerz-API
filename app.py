import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

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


@app.route('/', methods=['GET'])
def home():
    return "<h1>Blackerz Discord bot list API</h1><p>This site is a prototype API for discord bot list.</p>"

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Data tidak ditemukan, cek kembali URL.</p>", 404

@app.route('/api/v1/bots/all', methods=['GET'])
def api_all():
    if 'id' in request.args:
        idStr = request.args['id']
        if (not idStr.isnumeric()): 
            return "<h1>Input kueri id bukan sebuah angka</h1><p>Ubah kueri id ke angka.</p>"

        id = int(idStr)
        if id in bots:
            return jsonify(bots[id])
        else:
            return "<h1>404</h1><p>Bot tidak ditemukan</p>"
    else:
        return jsonify(bots) 

app.run()
