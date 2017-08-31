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
    try:
        fp = open(fileName, 'r')
        return set(line.strip() for line in fp)
    except IOError:
        fp = open(fileName, 'w+')
        return set()


def writeMatchIDToFile(ident, fileName):
	#f = open(fileName, 'a+')
    with open(fileName, 'a') as f:
        f.write(str(ident) + '\n')

#global vars
settings = []
with open('settings.json') as data_file:
    settings = json.load(data_file)

regex = re.compile('[%s]' % re.escape(string.punctuation))

#load data
internalList = readCsvAsListOfDictionaries(settings["internalListPath"], settings["internalListSeparator"])
externalList = readCsvAsListOfDictionaries(settings["externalListPath"], settings["externalListSeparator"])
matchedIDs = getMatchedSetFromFile(settings["matchedFileName"])

#voting functions
def majorityVoted(d):
    lst = [d["LevName"], d["DiffName"], d["SorName"], d["JacName"]]

    mappingIDs = {"LevName": "LevABA", "DiffName": "DiffABA", "SorName":"SorABA", "JacName":"JacABA"}
    mostCommonID = 0
    fieldNames = ["BaseID","BaseName","DiffABA","DiffName","DiffValue","LevABA","LevName","LevValue","SorABA","SorName","SorValue","JacABA","JacName","JacValue"]
    subDictionary = {key:d[key] for key in fieldNames}

    mostCommonName, mostCommonScore = Counter(lst).most_common(1)[0]
    for key, value in d.subDictionary():
        if value == mostCommonName and not key == "BaseName":
            mostCommonID = d[mappingIDs[key]]

    return {"MajorityVotedName" : mostCommonName, "MajorityVotedABA" : mostCommonID}

def fuzzyVoted(d):

    fieldNames = ["LevName", "DiffName", "SorName", "JacName"]
    mappingValues = {"LevName": "LevValue", "DiffName": "DiffValue", "SorName":"SorValue", "JacName":"JacValue"}
    mappingIDs = {"LevName": "LevABA", "DiffName": "DiffABA", "SorName":"SorABA", "JacName":"JacABA"}


    subDictionary = {key:d[key] for key in fieldNames}
    uniqueCounts = dict(Counter(subDictionary.values()).most_common())

    uniqueScores = {}
    uniqueIDs = {}

    for v in uniqueCounts.keys():
        for key, value in d.items():

            if value == v and not key == "BaseName" :
                if uniqueScores.get(v) == None:
                    uniqueScores[v] = 0
                uniqueScores[v] += d[mappingValues[key]]
                uniqueIDs[v] = d[mappingIDs[key]]

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

        if str(baseID) in matchedIDs:
            print("Skipping...Has a match...")
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
        summaryDic.update(majorityVoted(summaryDic))
        pprint.pprint(summaryDic)
        writeDicToFile(summaryDic, settings["outputFileName"])
        writeMatchIDToFile(baseID, settings["matchedFileName"])

#run from here
evaluateMatches()
