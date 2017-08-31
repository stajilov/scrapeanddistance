import csv
import pandas as pd
import codecs, difflib, Levenshtein, distance
import re
import string
import pprint
import json
from collections import Counter

import os.path

def readCsvAsListOfDictionaries(fName, separator):
    df = pd.read_csv(fName, error_bad_lines=False, sep=separator)
    return df.to_dict('records')

def getMatchedSetFromFile(fileName):
	return set(line.strip() for line in open(fileName, 'r'))

def writeMatchIDToFile(id, fileName):
	f = open(fileName, 'a+')
	f.write(id + '\n')
	f.close()


#global vars
settings = []
with open('settings.json') as data_file:
    settings = json.load(data_file)

regex = re.compile('[%s]' % re.escape(string.punctuation))

#load data
internalList = readCsvAsListOfDictionaries(settings["internalListPath"], settings["internalListSeparator"])
externalList = readCsvAsListOfDictionaries(settings["externalListPath"], settings["externalListSeparator"])
matchedIDs = getMatchedSetFromFile[settings["matchedFileName"]]

#voting functions
def majorityVoted(d):
    lst = [d["LevName"], d["DiffName"], d["SorName"], d["JacName"]]
    key, value = Counter(lst).most_common(1)[0]
    return key

def fuzzyVoted(d):

    fieldNames = ["LevName", "DiffName", "SorName", "JacName"]
    mappingValues = {"LevName": "LevValue", "DiffName": "DiffValue", "SorName":"SorValue", "JacName":"JacValue"}
    mappingIDs = {"LevName": "LevABA", "DiffName": "DiffABA", "SorName":"SorABA", "JacName":"JacABA"}


    subDictionary = {key:d[key] for key in fieldNames}
    print("subDictionary" , subDictionary)
    uniqueCounts = dict(Counter(subDictionary.values()).most_common())
    print("uniqueCounts", uniqueCounts)
    uniqueScores = {}
    uniqueIDs = {}

    for v in uniqueCounts.keys():
        for key, value in d.items():
            print("Checking key", key)
            print("Checking value", value)
            if value == v and not key == "BaseName" :
                print("value from unique counts", v)
                print("value from dictionary against which we're checking", value)
                if uniqueScores.get(v) == None:
                    uniqueScores[v] = 0
                print("checking key..", key)
                uniqueScores[v] += d[mappingValues[key]]
                uniqueIDs[v] = d[mappingIDs[key]]
    #pprint.pprint(uniqueCounts)
    #pprint.pprint(uniqueScores)
    resultDic = {k: uniqueScores[k] / uniqueCounts[k] for k in uniqueCounts if k in uniqueScores}
    resKey, resValue = Counter(resultDic).most_common(1)[0]

    return {"FuzyVotedName" : resKey, "FuzyVotedScore" : resValue, "FuzzyVotedABA" : uniqueIDs[resKey]}


#write matching result to the output file
def writeDicToFile(dic, fileName):
    fileExists = os.path.exists(fileName)
    with open(fileName, 'a+') as f:
        w = csv.DictWriter(f, dic.keys())
        if fileExists == False:
            w.writeheader()
        w.writerow(dic)


#preprocess token
def cleanString(s):
    return regex.sub('', s).lower()

#basic metrics function
def calsulateDistances(st1, st2):
    diffl = difflib.SequenceMatcher(None, st1, st2).ratio()
    lev = Levenshtein.ratio(st1, st2)
    sor = 1 - distance.sorensen(st1, st2)
    jac = 1 - distance.jaccard(st1, st2)
    return diffl, lev, sor, jac



def evaluateMatches():
    for internalProvider in internalList:
        baseName = internalProvider[settings["internalProviderNameColumn"]]
        baseState = internalProvider[settings["internalProviderStateColumn"]]
        baseID = internalProvider[settings["internalProviderIDColumn"]]

        if baseID in matchedIDs:
            print("Has a match")
            continue

        diffName = ""
        diffValue = 0
        diffABA = ""

        levName = ""
        levValue = 0
        levABA = ""

        sorName = ""
        sorValue = 0
        sorABA = ""

        jacName = ""
        jacValue = 0
        jacABA = ""

        for externalProvider in externalList:
            targetName = externalProvider[settings["externalProviderNameColumn"]]
            targetState = externalProvider[settings["externalProviderStateColumn"]]
            targetID = externalProvider[settings["externalProviderIDColumn"]]

            diff, lev, sor, jac = calsulateDistances(cleanString(baseName), cleanString(targetName))

            if diff > diffValue:
                diffValue = diff
                diffName = targetName
                diffABA = targetID

            if lev > levValue:
                levValue = lev
                levName = targetName
                levABA = targetID

            if sor > sorValue:
                sorValue = sor
                sorName = targetName
                sorABA = targetID

            if jac > jacValue:
                jacValue = jac
                jacName = targetName
                jacABA = targetID


        summaryDic = dict(zip(('BaseID', 'BaseName', 'DiffABA', 'DiffName', 'DiffValue', 'LevABA', 'LevName','LevValue','SorABA','SorName','SorValue','JacABA','JacName','JacValue'), (baseID, baseName, diffABA, diffName,diffValue,levABA, levName,levValue,sorABA, sorName, sorValue, jacABA, jacName, jacValue)))

        summaryDic.update(fuzzyVoted(summaryDic))
        summaryDic["MajorityVoted"] = majorityVoted(summaryDic)
        pprint.pprint(summaryDic)
        writeDicToFile(summaryDic, settings["outputFileName"])
        writeMatchIDToFile(baseID, settings["matchedFileName"])

#run from here
evaluateMatches()
