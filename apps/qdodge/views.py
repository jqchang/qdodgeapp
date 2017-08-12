from django.shortcuts import render, HttpResponse, redirect
import json
import urllib2
import numpy as np
import keys

API_ROOT_URL = r"https://na1.api.riotgames.com"
API_KEY = keys.API_KEY
CHAMP_DATA = r"/lol/static-data/v3/champions?locale=en_US&dataById=false&api_key="
MASTERY_DATA = r"/lol/champion-mastery/v3/champion-masteries/by-summoner/"
SUMM_BY_NAME = r"/lol/summoner/v3/summoners/by-name/"
MATCH_HISTORY = r"/lol/match/v3/matchlists/by-account/"
CURRENT_SEASON = r"9"
apicalls = 0

def getChampNames():
    global apicalls
    try:
        champs = json.loads(urllib2.urlopen(CHAMP_DATA+API_KEY).read())
        apicalls += 1
        return champs
    except urllib2.HTTPError as e:
        print e
        return []

def getPlayerNames(chatlog):
    names = []
    for i in chatlog.split('\n'):
        newname = i[:len(i)-22]
        newname = newname.replace(" ","%20")
        if len(names) < 5 and newname not in names:
            names.append(newname)
    return names

def getSummonerId(arr):
    global apicalls
    nameDict = {}
    for i in arr:
        data = json.loads(urllib2.urlopen(API_ROOT_URL+SUMM_BY_NAME+i+r"?api_key="+API_KEY).read())
        apicalls += 1
        # print data
        nameDict[data["name"]] = {"id":data["id"], "accountId":data["accountId"]}
    return nameDict

def getMasteryScores(summId):
    global apicalls
    data = json.loads(urllib2.urlopen(API_ROOT_URL+MASTERY_DATA+str(summId)+r"?api_key="+API_KEY).read())
    apicalls += 1
    return data

def getMatches(acctId):
    global apicalls
    data = json.loads(urllib2.urlopen(API_ROOT_URL+MATCH_HISTORY+str(acctId)+r"?season="+CURRENT_SEASON+r"&api_key="+API_KEY).read())
    apicalls += 1
    return data

# Create your views here.
def index(req):
    # champ_data = open('urls.py')
    # data1 = json.load(champ_data)
    # print champ_data
    # champ_data.close()
    return render(req, 'index.html')

def dodge(req):
    if req.method == 'GET':
        return redirect('/')
    elif req.method == 'POST':
        playerNames = getPlayerNames(req.POST["chat"])
        summId = getSummonerId(playerNames)
        for key,val in summId.items():
            mastery = getMasteryScores(val["id"])
            for i in mastery:
                print i
            summId[key]["numRanked"] = getMatches(val["accountId"])["totalGames"]
        return render(req, 'playerstats.html', {"players":summId})
