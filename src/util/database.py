from firebase import firebase
import requests, time, pymongo, pprint, json
from bson import ObjectId, json_util
from threading import Timer, Thread

firebaseDB = firebase.FirebaseApplication('https://blackerz-default-rtdb.firebaseio.com/', None)
client = pymongo.MongoClient("mongodb+srv://Fastering:35E8rQNJ93OboVUl@blackerz.ayxqe.mongodb.net/Infrastructure?authSource=admin&retryWrites=true&w=majority", connect=False)
dbInfrastructure = client.Infrastructure
dbAdmins = client.Admins
scannerWebhook = "https://second-solstice-medusaceratops.glitch.me/webchanges"

#dbInfrastructure.serverlist.create_index([('name', pymongo.TEXT)])

 
# CACHE'S
home_botCaches = {}


# STATIC FUNCTIONS
def deleteCache(tipe="botsverified"):
  if not tipe in home_botCaches: return False
  del home_botCaches[tipe]
  return True

def putCache(tipe, isi, lama=1000.0):
    home_botCaches[tipe] = isi
    Timer(lama, deleteCache, [tipe]).start()
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

def skiplimit(cursor, page_size=20, page_num=1):
    # Calculate number of documents to skip
    skips = page_size * (page_num - 1)
    # Skip and limit, Return documents
    return cursor.skip(skips).limit(page_size)
   
def nclamp(angka, kecil, maks):
    return kecil if angka < kecil else maks if angka > maks else angka 

# DATABASES
class mongoDB():
   def __init__(self, **anydata):
      self.botID = anydata.get('bot_id', None)
      self.serverID = anydata.get('server_id', None)
      self.userID = anydata.get('user_id', None)
      self.tujuan = anydata.get('tujuan', None)
      
   def getAllBots(self, **anydata):
      vrified = anydata.get('verified', True)
      page = nclamp(anydata.get('page', 1), 1, 10000)
      botc = home_botCaches.get("_botsverified")
      if botc and vrified:
         return list(botc[0]), botc[1]
      dt = skiplimit(dbInfrastructure.botlist.find({"verified": vrified}, {'_id': False}), 50, page)
      jmlh = dt.count(True)
      return list(putCache("_botsverified", [dt, jmlh], 700)[0]), jmlh
   
   def getAllServers(self, **anydata):
      page = nclamp(anydata.get('page', 1), 1, 10000)
      serverc = home_botCaches.get("_allservers")
      if serverc:
         return list(serverc[0]), serverc[1]
      dt = skiplimit(dbInfrastructure.serverlist.find({}, {'_id': False}), 20, page)
      jmlh = dt.count()
      return list(putCache("_allservers" + str(page), [dt, jmlh], 600)[0]), jmlh
   
   def botQuerySearch(self, **anydata):
      kueri = str(anydata.get('kueri', "")).replace("\\", "\\\\")
      page = nclamp(anydata.get('page', 1), 1, 10000)
      botqc = home_botCaches.get("_kueribot " + kueri)
      vrified = anydata.get('verified', True)
      if botqc and vrified:
         return list(botqc[0]), botqc[1]
      dt = skiplimit(dbInfrastructure.botlist.find({
         "$or": [ {"name": {'$regex': "^" + kueri, '$options': 'i'}}, {"ShortDescription": {'$regex': "^" + kueri, '$options': 'i'}} ], 
         "verified": vrified
      }, {'_id': False}), 20, page)
      jmlh = dt.count()
      data = list(putCache("_kueribot " + kueri, [dt, jmlh], 5)[0])
      return data, jmlh
   
   def serverQuerySearch(self, **anydata):
      kueri = str(anydata.get('kueri', "")).replace("\\", "\\\\")
      page = nclamp(anydata.get('page', 1), 1, 10000)
      serverqc = home_botCaches.get("_kueriserver " + kueri)
      if serverqc:
         return list(serverqc[0]), serverqc[1]
      dt = skiplimit(dbInfrastructure.serverlist.find({
         "$or": [ {"name": {'$regex': "^" + kueri, '$options': 'i'}}, {"ShortDescription": {'$regex': "^" + kueri, '$options': 'i'}} ]
      }, {'_id': False}), 20, page)
      jmlh = dt.count()
      data = list(putCache("_kueriserver " + kueri, [dt, jmlh], 5)[0])
      return data, jmlh 
   
   def AutocorrectSearchBot(self, **anydata):
      return dbInfrastructure.botlist.find({"$text": {"$search": anydata.get('kueri', "bot").replace("\\", "\\\\") }}, {"name": 1, "_id": 0, "id": 1}).limit(anydata.get("limit", 10))
      #return dbInfrastructure.botlist.aggregate([
            #{
                #"$search": {
                    #"autocomplete": {
                        #"query": anydata.get('kueri', "bot"),
                        #"path": "name",
                        #"fuzzy": {
                            #"maxEdits": 2,
                            #"prefixLength": 3
                        #}
                    #}
                #}
            #}
        #])
        
   def AutocorrectSearchServer(self, **anydata):
      return dbInfrastructure.serverlist.find({"$text": {"$search": anydata.get('kueri', "server").replace("\\", "\\\\") }}, {"name": 1, "_id": 0, "id": 1}).limit(anydata.get("limit", 10))
     
   def uploadServer(self, **anydata):
      serverid = str(anydata.get('id', None))
      data = dict(anydata.get('data', {}))
      if serverid == "None": return False
      data["id"] = serverid
      warns = []
      oldserverdata = dbInfrastructure.serverlist.find_one({"id": serverid})
      if "upvotes" in data:
         del data['upvotes'] 
      if "icon" in data and (not isinstance(data['icon'], str) or (isinstance(data['icon'], str) and isLinkExist('https://cdn.discordapp.com/icons/' + serverid + '/' + data['icon']) == False)): 
         del data['icon']
         warns.append("Icon URL doesn't exist")
      if (not isinstance(data.get("ShortDescription"), str) or len(data['ShortDescription']) > 120): 
         del data['ShortDescription']
         warns.append("ShortDescription must lower than 120 length characters string")
      if data.get("memberCount") and (not isinstance(data['memberCount'], int) or data['memberCount'] > 10000000 or data['memberCount'] < 1): #("memberCount" in data and (not isinstance(data['memberCount'], int)) or data['memberCount'] > 10000000 or data['memberCount'] < 0):
         del data['memberCount']
         warns.append("Invalid memberCount")
      if data.get("joinLink") and (not isinstance(data['joinLink'], str) or len(data['joinLink']) > 16 or len(data['joinLink']) < 2):
         del data['joinLink']
         warns.append("Invalid joinLink")
      datatopush = {}
      if oldserverdata: 
         if not "upvotes" in oldserverdata: datatopush['upvotes'] = 0
         if "id" in data and not "id" in oldserverdata: datatopush['id'] = data['id'] 
      if data.get("name"): datatopush['name'] = data['name']
      if data.get("icon"): datatopush['icon'] = data['icon']
      if data.get("memberCount"): datatopush['memberCount'] = data['memberCount']
      if data.get("joinLink"): datatopush["joinLink"] = data["joinLink"]
      if data.get("ShortDescription"): datatopush['ShortDescription'] = data['ShortDescription'] 
      if data.get("LongDescription"): datatopush['LongDescription'] = data['LongDescription'] 
      if data.get("owner"): 
         if data["owner"].get("id"): 
            if not "owner" in datatopush: datatopush["owner"] = {}
            datatopush["owner"]["id"] = data["owner"]["id"]
         if data["owner"].get("name"): 
            if not "owner" in datatopush: datatopush["owner"] = {}
            datatopush["owner"]["name"] = data["owner"]["name"]
      try:
         result = dbInfrastructure.serverlist.update_one({"id": serverid}, { "$set": datatopush }, upsert=True)
         return result, {"sucess": True, "warns": warns}
      except Exception as keslhn:
         print(keslhn)
         return None, {"sucess": False, "warns": warns, "error": "Internal Server Error, please report the bug."}
   
   def uploadBot(self, **anydata):
      botid = str(anydata.get('id', None))
      data = anydata.get('data', {})
      for kdata in list(data):
         if data.get(kdata) == None: del data[kdata]
      data["id"] = botid
      try:
         result = dbInfrastructure.botlist.update_one({"id": botid}, { "$set": data }, upsert=True)
         return result, {"sucess": True, "warns": []}
      except Exception as keslhn:
         print(keslhn)
         return None, {"sucess": False, "warns": warns, "error": "Internal Server Error, please report the bug."}
        
   def uploadUser(self, **anydata):
      userid = str(anydata.get('id', None))
      data = dict(anydata.get('data', {}))
      for kdata in data:
         if data.get(kdata) == None: del data[kdata]
      try:
         result = dbInfrastructure.users.update_one({"id": userid}, { "$set": data }, upsert=True)
         return result, {"sucess": True, "warns": []}
      except Exception as keslhn:
         print(keslhn)
         return None, {"sucess": False, "warns": warns, "error": "Internal Server Error, please report the bug."}
   
   def addVote(self, **anydata):
      tipe = anydata.get('tipe', "botlist")
      id = str(anydata.get('id', None))
      if not id: return False
      try:
         result = dbInfrastructure[tipe].update({'id': id}, {'$inc': {'upvotes': 1}})
         return True, result
      except Exception as keslhn:
         print(keslhn)
         return False, keslhn
   
   def is_ownerof(self, **anydata):
      authv1 = anydata.get('auth', None)
      tipeasset = anydata.get('tipe', "botlist")
      assetid = anydata.get('aset', None)
      if not authv1: return {"success": False, "reason": "Unauthorized, Please put Authoriation headers"}
      user = dbInfrastructure.users.find_one({"AuthorizationV1": str(authv1)} if isinstance(authv1, str) else authv1)
      print(user)
      if not user: return {"success": False, "reason": "Unauthorized, User doesnt exist"}
      owned = dbInfrastructure[tipeasset].find_one({"owner.id": str(user["id"]), "id": assetid}, {'_id': False})
      print(owned)
      print(user["id"])
      if owned == None: return {"success": False, "reason": "Unauthorized, asset not owned"}
      return {"success": True, "reason": "success", "aset": owned, "user": user}
   
   def get_owned(self, **anydata):
      if home_botCaches.get("owned " + str(anydata)):
         return home_botCaches.get("owned " + str(anydata))
      tipe = anydata.get('tipe', "botlist")
      userid = anydata.get('id', None)
      if userid == None: return []
      return putCache("owned " + str(anydata), list(dbInfrastructure[tipe].find({"owner.id": userid})), 25)
     
   def get_server(self, **find):
      if home_botCaches.get("server " + str(find)):
         return home_botCaches.get("server " + str(find))
      return putCache("server " + str(find), dbInfrastructure.serverlist.find_one(find, {'_id': False}), 2.5)
    
   def get_bot(self, **find):
      if home_botCaches.get("bot " + str(find)):
         return home_botCaches.get("bot " + str(find))
      return putCache("bot " + str(find), dbInfrastructure.botlist.find_one(find, {'_id': False}), 2)
  
   def get_user(self, **find):
      if home_botCaches.get("user " + str(find)):
         return home_botCaches.get("user " + str(find))
      return putCache("user " + str(find), dbInfrastructure.users.find_one(find, {'_id': False}), 20)
     
   def delete_bot(self, **find):
      return dbInfrastructure.botlist.delete_one(find)

class IdentifyApiUser():
   def __init__(self, **anydata):
      self.apikey = anydata.get('apikey', None)
      self.izin = {"all": False, "bumpserver": False, "editbot": False}
    
   def get_user(self, **anydata):
      self.data = dbAdmins.users.find_one({"apikey": anydata.get('apikey', self.apikey)}, {'_id': False})
      if isinstance(self.data, dict) and self.data.get("allow"):
         for izin in (self.data["allow"].split(";")):
            if len(izin) >= 1: self.izin[izin] = True    
      
      return self
   
     
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
      
def send_webhook(link, body):
    return requests.post(link, json = body)
  
  
  
