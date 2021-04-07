import pickle
import codecs
import re
import time
from os import path

st = time.time()
path = path.abspath(path.dirname(__file__))

ASConfidence = {}
ASFinalConfidence = {}

with open(path + "\..\Pickles\IRR.pickle", "rb") as p:
    IRRimpexp = pickle.load(p)
with open(path + "\..\Pickles\IRRv2.pickle", "rb") as p:
    IRRremarks = pickle.load(p)
with open(path + "\..\Pickles\IRRv3.pickle", "rb") as p:
    IRRsets = pickle.load(p)

count1 = 0
count05 = 0
count07 = 0


def needtostart():
    global count1
    global count05
    global count07
    for key in list(set(list(IRRimpexp.keys())+list(IRRimpexp.keys())+list(IRRimpexp.keys()))):
        if key[0] not in ASConfidence.keys():
            ASConfidence[key[0]] = []

        if key in IRRremarks.keys() and key in IRRsets.keys() and key in IRRimpexp.keys():
            if IRRremarks[key] == IRRimpexp[key] and IRRsets[key] == IRRimpexp[key]:
                ASConfidence[key[0]].append(1)
            elif IRRremarks[key] == IRRsets[key] and IRRsets[key] != IRRimpexp[key]:
                ASConfidence[key[0]].append(0.85)
            elif IRRremarks[key] != IRRsets[key] and (IRRimpexp[key] == IRRsets[key] or IRRimpexp[key] == IRRremarks[key]):
                ASConfidence[key[0]].append(0.6)
            else:
                ASConfidence[key[0]].append(0.1)

        elif key in IRRremarks.keys() and key  not in IRRsets.keys() and key in IRRimpexp.keys():
            if IRRremarks[key] == IRRimpexp[key]:
                ASConfidence[key[0]].append(0.75)
            else:
                ASConfidence[key[0]].append(0.3)

        elif key not in IRRremarks.keys() and key in IRRsets.keys() and key in IRRimpexp.keys():
            if IRRsets[key] == IRRimpexp[key]:
                ASConfidence[key[0]].append(0.75)
            else:
                ASConfidence[key[0]].append(0.3)

        elif key not in IRRremarks.keys() and key not in IRRsets.keys() and key in IRRimpexp.keys():
            if IRRimpexp[key] == "Unknown":
                ASConfidence[key[0]].append(0)
            else:
                ASConfidence[key[0]].append(0.5)

        elif key in IRRremarks.keys() and key in IRRsets.keys() and key not in IRRimpexp.keys():
            if IRRremarks[key] == IRRsets[key]:
                ASConfidence[key[0]].append(0.8)
            else:
                ASConfidence[key[0]].append(0.1)

        elif key in IRRremarks.keys() and key not in IRRsets.keys() and key not in IRRimpexp.keys():
            ASConfidence[key[0]].append(0.6)

        elif key not in IRRremarks.keys() and key in IRRsets.keys() and key not in IRRimpexp.keys():
            ASConfidence[key[0]].append(0.6)

    for key in ASConfidence.keys():
        confidence = round(sum(ASConfidence[key])/len(ASConfidence[key]), 2)
        ASFinalConfidence[key] = confidence
        if confidence == 1:
            count1 += 1
        if confidence >= 0.5:
            count05 += 1
        if confidence >= 0.7:
            count07 += 1


needtostart()
print(ASFinalConfidence)
print(round(float(count1)/len(ASFinalConfidence.keys()), 2))
print(round(float(count05)/len(ASFinalConfidence.keys()), 2))
print(round(float(count07)/len(ASFinalConfidence.keys()), 2))


with open(path + "/../Pickles/StartConfidence.pickle", "wb") as p:
    pickle.dump(ASFinalConfidence, p)
