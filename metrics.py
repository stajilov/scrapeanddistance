import csv
import pandas as pd
import codecs, difflib, Levenshtein, distance
import re
import string

def readCsvAsListOfDictionaries(fName):
    df = pd.read_csv(fName, error_bad_lines=False)
    return df.to_dict('records')

regex = re.compile('[%s]' % re.escape(string.punctuation))
internalList = readCsvAsListOfDictionaries("institutions_new.csv")
externalList = readCsvAsListOfDictionaries("3rdparty.csv")


def writeDicToFile(dic, fileName):
    


def cleanString(s):
    return regex.sub('', s).lower()


def calsulateDistances(st1, st2):
    sr = row.lower().split("\t")
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










evaluateMatches()
