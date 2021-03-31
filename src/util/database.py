from firebase import firebase
import requests, time

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)

class data():
    def __init__(self, dataName):
        firebaseDB = firebase.FirebaseApplication(
            'https://blackerz-default-rtdb.firebaseio.com/', None)
        result = firebaseDB.get('/Infrastructure/botlist', None)
        print(result)
        self.data = result

def notifyWebhook(botId, voter):
    try:
        url = firebaseDB.get('/PrivateData/bots/' + str(botId) + "/webhooks/url", None)
        if url == None: return False
        requests.post(url, data = {"vote": {"userid": str(voter), "date": time.time() * 1000}}, headers={"user-agent": "Blackerz/1.0"},timeout=20)
        return True
    except Exception as kesalahan:
        print(kesalahan)
        return False
