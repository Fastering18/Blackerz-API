from firebase import firebase
import requests, time, pymongo, pprint
from threading import Timer, Thread

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
client = pymongo.MongoClient("mongodb+srv://Fastering:35E8rQNJ93OboVUl@blackerz.ayxqe.mongodb.net/Infrastructure?authSource=admin&retryWrites=true&w=majority", connect=False)
dbInfrastructure = client.Infrastructure
scannerWebhook = "https://scanner-blackerz-discord.glitch.me/webchanges"

 
# CACHE'S
home_botCaches = {}


# STATIC FUNCTIONS
def deleteCache(tipe="botsverified"):
  if not tipe in home_botCaches: return False
  del home_botCaches[tipe]
  return True

def putCache(tipe, isi):
    home_botCaches[tipe] = isi
    Timer(1000.0, deleteCache, [tipe]).start()
    return isi
   
def isLinkExist(link):
    exist = requests.get(link)
    return exist.status_code != 404
  
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
class mongoDB():
   def __init__(self, **anydata):
      self.botID = anydata.get('bot_id', None)
      self.serverID = anydata.get('server_id', None)
      self.userID = anydata.get('user_id', None)
      self.tujuan = anydata.get('tujuan', None)
      
   def getAllBots(self, **anydata):
      vrified = anydata.get('verified', True)
      if "botsverified" in home_botCaches and vrified:
         return home_botCaches["botsverified"]
      data = putCache("botsverified", list(dbInfrastructure.botlist.find({"verified": vrified})))
      return data
   
   def getAllServers(self, **anydata):
      if "_allservers" in home_botCaches:
         return home_botCaches["_allservers"]
      data = putCache("_allservers", list(dbInfrastructure.serverlist.find({}, limit=20)))
      return data
   
   def botQuerySearch(self, **anydata):
      kueri = str(anydata.get('kueri', ""))
      vrified = anydata.get('verified', True)
      data = list(dbInfrastructure.botlist.find({
         "$or": [ {"name": {'$regex': kueri, '$options': 'i'}}, {"ShortDescription": {'$regex': kueri, '$options': 'i'}} ], 
         "verified": vrified
      }, limit=30))
      return data
   
   def serverQuerySearch(self, **anydata):
      kueri = str(anydata.get('kueri', ""))
      data = list(dbInfrastructure.serverlist.find({
         "$or": [ {"name": {'$regex': kueri, '$options': 'i'}}, {"ShortDescription": {'$regex': kueri, '$options': 'i'}} ]
      }, limit=30))
      return data
   
   def uploadServer(self, **anydata):
      serverid = str(anydata.get('id', None))
      data = anydata.get('data', {})
      if serverid == "None": return False
      data["id"] = serverid
      warns = []
      oldserverdata = dbInfrastructure.serverlist.find_one({"id": serverid})
      if "upvotes" in data:
         del data['upvotes'] 
      if "icon" in data and (not isinstance(data['icon'], str) or (isinstance(data['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + serverid + '/' + data['icon']) == False)): 
         del data['icon']
         warns.append("Icon URL doesn't exist")
      if ("ShortDescription" in data and (not isinstance(data['ShortDescription'], str) or len(data['ShortDescription']) > 120)): 
         del data['ShortDescription']
         warns.append("ShortDescription must lower than 120 length characters string")
      if ("memberCount" in data and (not isinstance(data['memberCount'], int)) or data['memberCount'] > 10000000 or data['memberCount'] < 0):
         del data['memberCount']
         warns.append("Invalid memberCount")
      if "joinLink" in data and (not isinstance(data['joinLink'], str) or len(data['joinLink']) > 16 or len(data['joinLink']) < 2):
         del data['joinLink']
         warns.append("Invalid joinLink")
      datatopush = {}
      if oldserverdata: 
         if not "upvotes" in oldserverdata: datatopush['upvotes'] = 0
         if "id" in data and not "id" in oldserverdata: datatopush['id'] = data['id'] 
      if "name" in data: datatopush['name'] = data['name']
      if "icon" in data: datatopush['icon'] = data['icon']
      if "memberCount" in data: datatopush['memberCount'] = data['memberCount']
      if "ShortDescription" in data: datatopush['ShortDescription'] = data['ShortDescription'] 
      if "LongDescription" in data: datatopush['LongDescription'] = data['LongDescription'] 
      if "owner" in data: 
         if "id" in data["owner"]: 
            if not "owner" in datatopush: datatopush["owner"] = {}
            datatopush["owner"]["id"] = data["owner"]["id"]
         if "name" in data["owner"]: 
            if not "owner" in datatopush: datatopush["owner"] = {}
            datatopush["owner"]["name"] = data["owner"]["name"]
      try:
         result = dbInfrastructure.serverlist.update_one({"id": serverid}, { "$set": data }, upsert=True)
         return result, {"sucess": True, "warns": warns}
      except Exception as keslhn:
         print(keslhn)
         return None, {"sucess": False, "warns": warns, "error": "Internal Server Error, please report the bug."}
        
   def get_server(self, **find):
      return dbInfrastructure.serverlist.find_one(find)
    
   def get_bot(self, **find):
      return dbInfrastructure.botlist.find_one(find)
   
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
  
  
  
