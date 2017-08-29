import csv
import pandas as pd
import codecs, difflib, Levenshtein, distance
import re
import string
import pprint
from collections import Counter

import os.path

def readCsvAsListOfDictionaries(fName):
    df = pd.read_csv(fName, error_bad_lines=False)
    return df.to_dict('records')

settings = []
with open('settings.json') as data_file:
    settings = json.load(data_file)

regex = re.compile('[%s]' % re.escape(string.punctuation))

internalList = readCsvAsListOfDictionaries(settings["internalListPath"])
externalList = readCsvAsListOfDictionaries(settings["externalListPath"])



def majorityVoted(d):
    lst = [d["LevName"], d["DiffName"], d["SorName"], d["JacName"]]
    key, value = Counter(lst).most_common(1)[0]
    return key

def fuzzyVoted(d):

    fieldNames = ["LevName", "DiffName", "SorName", "JacName"]
    mapping = {"LevName": "LevValue", "DiffName": "DiffValue", "SorName":"SorValue", "JacName":"JacValue"}


    subDictionary = {key:d[key] for key in fieldNames}
    uniqueCounts = dict(Counter(subDictionary.values()).most_common())
    uniqueScores = {}

    for v in uniqueCounts.keys():
        for key, value in d.items():
            if value == v:
                if uniqueScores.get(v) == None:
                    uniqueScores[v] = 0
                uniqueScores[v] += d[mapping[key]]
    pprint.pprint(uniqueCounts)
    pprint.pprint(uniqueScores)
    resultDic = {k: uniqueScores[k] / uniqueCounts[k] for k in uniqueCounts if k in uniqueScores}
    key, value = Counter(resultDic).most_common(1)[0]
    #print(key, value)

    return {"FuzyVotedName" : key, "FuzyVotedScore" : value}



def writeDicToFile(dic, fileName):
    fileExists = os.path.exists(fileName)
    with open(fileName, 'a+') as f:
        w = csv.DictWriter(f, dic.keys())
        if fileExists == False:
            w.writeheader()
        w.writerow(dic)



def cleanString(s):
    return regex.sub('', s).lower()


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

        diffName = ""
        diffValue = 0
        levName = ""
        levValue = 0
        sorName = ""
        sorValue = 0
        jacName = ""
        jacValue = 0

        for externalProvider in externalList:
            targetName = externalProvider[settings["externalProviderNameColumn"]]
            targetState = externalProvider[settings["externalProviderStateColumn"]]

            diff, lev, sor, jac = calsulateDistances(cleanString(baseName), cleanString(targetName))

            if diff > diffValue:
                diffValue = diff
                diffName = targetName
            if lev > levValue:
                levValue = lev
                levName = targetName

            if sor > sorValue:
                sorValue = sor
                sorName = targetName

            if jac > jacValue:
                jacValue = jac
                jacName = targetName


        summaryDic = dict(zip(('BaseName', 'DiffName', 'DiffValue', 'LevName','LevValue','SorName','SorValue','JacName','JacValue'), (baseName,diffName,diffValue,levName,levValue,sorName, sorValue, jacName, jacValue)))

        summaryDic.update(fuzzyVoted(summaryDic))
        summaryDic["MajorityVoted"] = majorityVoted(summaryDic)
        pprint.pprint(summaryDic)
        writeDicToFile(summaryDic, settings["outputFileName"])



evaluateMatches()
