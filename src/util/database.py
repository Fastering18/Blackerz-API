from firebase import firebase
import requests, time, pymongo
from threading import Timer, Thread

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
client = pymongo.MongoClient("mongodb+srv://Fastering:35E8rQNJ93OboVUl@blackerz.ayxqe.mongodb.net/Infrastructure?authSource=admin&retryWrites=true&w=majority")
dbInfrastructure = client.Infrastructure
scannerWebhook = "https://scanner-blackerz-discord.glitch.me/webchanges"

print(db.command("serverStatus"))
#for server in db.serverlist.find({}):
   #print(server)
serverlist = firebaseDB.get("/Infrastructure/serverlist")
for server in serverlist:
   if db.serverlist.find_one({"id": server}) == None:
      db.serverlist.insert_one(serverlist[server])
   
# CACHE'S
home_botCaches = {}


# STATIC FUNCTIONS
def deleteCache(tipe="botsverified"):
  if not tipe in home_botCaches: return False
  del home_botCaches[tipe]
  return True

def putCache(tipe, isi):
    home_botCaches[tipe] = isi
    Timer(6000.0, deleteCache, [tipe]).start()
    return True

def sortBy(dic, tipe="upvotes"):
    daftr = [] #list(dic.values())
    for keyy in dic:
        vInside = dic[keyy]
        vInside["id"] = keyy
        daftr.append(vInside)
    daftr.sort(key=lambda ddata: ddata.get(tipe, 0), reverse=True)
    daftr.sort(key=lambda ddata: ddata.get("id"))
    return daftr


# DATABASES
class dataManager():
    def __init__(self, **anydata):
        self.botID = anydata.get('bot_id', None)
        self.serverID = anydata.get('server_id', None)
        self.userID = anydata.get('user_id', None)
        self.tujuan = anydata.get('tujuan', None)
        
    def getAllBots(self, **anydata):
        if "botsverified" in home_botCaches:
            self.data = home_botCaches["botsverified"]
            return self.data
        try:
            result = requests.get('https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy=%22verified%22&equalTo=true').json() 
            self.data = sortBy(result)
            putCache("botsverified", self.data)
        except Exception as kesalahan:
            print(kesalahan)
            try:
                result = firebaseDB.get('/Infrastructure/botlist?orderBy=%22verified%22&equalTo=true', None)
                self.data = sortBy(result)
            except Exception as kesalahan2:
                print(kesalahan2)
                self.data = "Internal error, this is not your error, please report this issues to github."
        return self.data
    
    def botQuerySearch(self, **anydata):
        kueri = Data.get('kueri', "bot")
        self.filter = "verified"
        if kueri + "_querysearch" in home_botCaches:
            self.data = home_botCaches[kueri + "_querysearch"]
            return self.data
        try: 
            self.data = requests.get(f'https://blackerz-default-rtdb.firebaseio.com/Infrastructure/botlist.json?orderBy="{self.filter}"&equalTo=true').json()
            if kueri:
                listres = [] 
                for kunci in self.data:
                    if self.data[kunci]["name"].lower().startswith(kueri.lower()) or (kueri.lower() in self.data[kunci]["name"].lower()):
                        self.data[kunci]["id"] = kunci
                        listres.append(self.data[kunci])
                self.data = listres
                putCache(kueri + "_querysearch", self.data)
        except Exception as kesalahan:
            print(kesalahan)
            self.data = self.getAllBots()
        return self.data
    
    def postUserStats(self, **anydata):
        user = anydata.get('user', None)
        if user == None: return None
        self.data = {}
        self.data["tag"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "tag", user["tag"])
        self.data["avatar"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "avatar", user["avatar"])
        self.data["username"] = firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "username", user["username"])
        authV1 = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/AuthorizationV1", None)
        reatedAt = firebaseDB.get('/Infrastructure/WebUsers/' + user["client_id"] + "/CreatedAt", None)
        if authV1 == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "AuthorizationV1", generateAuthorizationV1())
        if createdAt == None : firebaseDB.put('/Infrastructure/WebUsers/' + user["client_id"], "CreatedAt", datetime.datetime.now().isoformat())
        return self.data

def notifyWebhook(botId, voter):
    try:
        datahook = firebaseDB.get('/PrivateData/bots/' + str(botId) + "/webhooks", None)
        if datahook == None: return False
        requests.post(datahook.get("url"), json = {"vote": {"id": str(voter), "date": time.time() * 1000}}, headers={"user-agent": "Blackerz/1.0", "Authorization": datahook.get("key")},timeout=20)
        return True
    except Exception as kesalahan:
        print(kesalahan)
        return False

def notifyChanges(text, itemId):
    try:
        print(requests.post(scannerWebhook, json = {"text": text, "date": time.time() * 1000, "itemId": itemId}, headers={"user-agent": "Blackerz/1.0", "Authorization": "menggokileak"},timeout=60).text)
        return True
    except Exception as kesalahan:
        print(kesalahan)
        return False
  
  
  
