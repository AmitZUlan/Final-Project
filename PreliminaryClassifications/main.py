import pickle
import re
import time
from os import path

st = time.time()
path = path.abspath(path.dirname(__file__))
ASDict = {}
with open(path + "\..\Pickles\ASDictv2.pickle", "rb") as p:
    ASDict = pickle.load(p)

i = 0
ASNum = 0
IRR = {}
x = 0
Unknown = 0
for AS1, impexpdict in ASDict.items():
    ASNum = ASNum + 1
    print(time.time() - st)
    impdict = impexpdict[0]
    expdict = impexpdict[1]
    for AS2 in impdict.keys():
        if AS1 == AS2:
            continue
        if not AS1.startswith("AS") or not AS1[2:].isnumeric() or not AS2.startswith("AS") or not AS2[2:].isnumeric():
            i = i + 1
        key = (AS1, AS2)
        if AS2 not in expdict.keys() or impdict[AS2] == "Error" or expdict[AS2] == "Error":
            IRR[key] = "Unknown"
            Unknown = Unknown + 1
        elif impdict[AS2] == 'A' and expdict[AS2] != 'A':
            IRR[key] = "C2P"
        elif impdict[AS2] != 'A' and expdict[AS2] == 'A':
            IRR[key] = "P2C"
        elif impdict[AS2] != 'A' and expdict[AS2] != 'A':
            IRR[key] = "P2P"
        else:
            IRR[key] = "P2C"
    for AS2 in expdict.keys():
        key = (AS1, AS2)
        if AS2 not in impdict.keys():
            IRR[key] = "Unknown"
            Unknown = Unknown + 1

# for AS1, impexpdict in ASDict.items():
#     impdict = impexpdict[0]
#     expdict = impexpdict[1]
#     for AS2 in impdict.keys():
#         key = (AS1, AS2)
#         revkey = (AS2, AS1)
#         if key in IRR.keys() and revkey in IRR.keys():
#             if IRR[key] == 'P2C' and IRR[revkey] != 'C2P':
#                 IRR[key] = "Conflict"
#                 IRR[revkey] = "Conflict"
#             if IRR[key] == 'C2P' and IRR[revkey] != 'P2C':
#                 IRR[key] = "Conflict"
#                 IRR[revkey] = "Conflict"
#             if IRR[key] == 'P2P' and IRR[revkey] != 'P2P':
#                 IRR[key] = "Conflict"
#                 IRR[revkey] = "Conflict"

print(IRR)
print(i)
print(ASNum)
print(Unknown)
print(len(list(IRR.keys())))

with open(path + "/../Pickles/IRR.pickle", "wb") as p:
    pickle.dump(IRR, p)
with open(path + "/../Example Files/IRRDict.txt", "w") as f:
    for k, v in IRR.items():
        f.write(str(k) + ": " + str(v) + "\n")