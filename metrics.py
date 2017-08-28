import csv
import pandas as pd
import codecs, difflib, Levenshtein, distance
import re
import string
from collections import Counter

import os.path

def readCsvAsListOfDictionaries(fName):
    df = pd.read_csv(fName, error_bad_lines=False)
    return df.to_dict('records')

regex = re.compile('[%s]' % re.escape(string.punctuation))
internalList = readCsvAsListOfDictionaries("institutions_new.csv")
externalList = readCsvAsListOfDictionaries("3rdparty.csv")


def majorityVoted(d):
    lst = [d["LevName"], d["DiffName"], d["SorName"], d["JacName"]]
    key, value = Counter(lst).most_common(1)[0]
    print(key)
    return key


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
        baseName = internalProvider["Name"]
        baseState = internalProvider["State"]

        diffName = ""
        diffValue = 0
        levName = ""
        levValue = 0
        sorName = ""
        sorValue = 0
        jacName = ""
        jacValue = 0

        for externalProvider in externalList:
            targetName = externalProvider["NAME"]
            targetState = externalProvider["STATE"]

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

        print(summaryDic)
        summaryDic["MajorityVoted"] = majorityVoted(summaryDic)
        writeDicToFile(summaryDic, "matching_results.csv")












evaluateMatches()
