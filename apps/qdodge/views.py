from django.shortcuts import render, HttpResponse, redirect
import json, os
import urllib2
import urllib
import numpy as np
import keys
import datetime

API_ROOT_URL = r"https://na1.api.riotgames.com"
API_KEY = keys.API_KEY
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAMP_DATA = r"/lol/static-data/v3/champions?locale=en_US&dataById=false&api_key="
MASTERY_DATA = r"/lol/champion-mastery/v3/champion-masteries/by-summoner/"
SUMM_BY_NAME = r"/lol/summoner/v3/summoners/by-name/"
MATCH_HISTORY = r"/lol/match/v3/matchlists/by-account/"
CURRENT_SEASON = r"9"
apicalls = 0
champ_data = open(os.path.join(BASE_DIR, 'qdodge/static/champions.json'),'r')
CHAMPS = json.loads(champ_data.read())["data"]
champ_data.close()

# def getChampNames():
#     global apicalls
#     try:
#         champs = json.loads(urllib2.urlopen(CHAMP_DATA+API_KEY).read())
#         apicalls += 1
#         return champs
#     except urllib2.HTTPError as e:
#         print e
#         return []

# NOW HANDLED ON FRONTEND JQUERY
# def getPlayerNames(chatlog):
#     names = []
#     for i in chatlog.split('\n'):
#         newname = i[:len(i)-22]
#         newname = newname.replace(" ","%20")
#         if len(names) < 5 and newname not in names:
#             names.append(newname)
#     return names

def getSummonerId(players):
    global apicalls
    # nameDict = {}
    for k,v in players.items():
        # print API_ROOT_URL+SUMM_BY_NAME+v["name"].replace(" ","%20")+r"?api_key="+API_KEY
        data = json.loads(urllib2.urlopen(API_ROOT_URL+SUMM_BY_NAME+v["name"].replace(" ","%20")+r"?api_key="+API_KEY).read())
        apicalls += 1
        # print data
        players[k]["id"] = data["id"]
        players[k]["accountId"] = data["accountId"]
        # nameDict[data["name"]] = {"id":data["id"], "accountId":data["accountId"]}
    # return nameDict

def getMasteryScores(summId):
    global apicalls
    data = json.loads(urllib2.urlopen(API_ROOT_URL+MASTERY_DATA+str(summId)+r"?api_key="+API_KEY).read())
    sanitized = {}
    apicalls += 1
    for i in data:
        sanitized[i["championId"]] = {
            "championPoints": i["championPoints"],
            "lastPlayTime": i["lastPlayTime"]
        }
    return sanitized

def getMatches(acctId):
    global apicalls
    try:
        data = json.loads(urllib2.urlopen(API_ROOT_URL+MATCH_HISTORY+str(acctId)+r"?season="+CURRENT_SEASON+r"&api_key="+API_KEY).read())
        apicalls += 1
        return data
    except urllib2.HTTPError as e:
        print # coding=utf-8
        return {"matches":[]}

# Create your views here.
def index(req):

    # data1 = json.load(champ_data)
    # print champ_data
    # champ_data.close()
    return render(req, 'index.html')

def dodge(req):
    if req.method == 'GET':
        return redirect('/')
    elif req.method == 'POST':
        global CHAMPS
        champlist = CHAMPS.items()
        champlist.sort(key=lambda x:int(x[0]))
        lanes = {}
        all_mastery = {}
        for i in "12345":
            lanes[req.POST["lane"+i]] = {"name":req.POST["summoner"+i]}
        getSummonerId(lanes)
        for k,v in lanes.items():
            lanes[k]["mastery"] = getMasteryScores(v["id"])
            lanes[k]["matches"] = getMatches(v["accountId"])
        for i in champlist:
            mastery = [0,0,0,0,0]
            # print i[1]["id"], i[1]["name"]
            for j,k in enumerate(["Top","Jungle","Mid","ADC","Support"]):
                try:
                    mastery[j] = (lanes[k]["mastery"][i[1]["id"]]["championPoints"],lanes[k]["mastery"][i[1]["id"]]["lastPlayTime"])
                except KeyError as e:
                    mastery[j] = (0,0)
            all_mastery[i[1]["id"]] = np.ravel(np.array(mastery))
        masterylist = []
        for k,v in all_mastery.items():
            masterylist.append(list(v))
        X = np.array(masterylist)
        print X, X.shape
        # ["name"], lanes["Top"]["mastery"]["105"]

        # for key,val in summId.items():
        #     mastery = getMasteryScores(val["id"])
        #     matches = getMatches(val["accountId"])
        #     for i in mastery:
        #         print i
        #     summId[key]["numRanked"] = matches["totalGames"]
        return render(req, 'playerstats.html', {"lanes":lanes})
        # return HttpResponse("lol")
