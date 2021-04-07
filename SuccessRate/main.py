import pickle
import re
import time
import csv
from os import path

path = path.abspath(path.dirname(__file__))
IRR = {}
Ref = {}
with open(path + "\..\Pickles\IRR_PreFinalA.pickle", "rb") as p:
    IRR = pickle.load(p)
with open(path + "\..\Pickles\IRR.pickle", "rb") as p:
    IRR2 = pickle.load(p)
with open(path + "\..\Pickles\Ref.pickle", "rb") as p:
    Ref = pickle.load(p)

matching_classifications = 0
number_of_ASNs_in_our_IRR = 0
number_of_ASNs_in_ref_IRR = 0
number_of_ASNs_in_our_and_ref_IRR = 0
knownkeysinboth = 0
correct = 0
notcorrect = 0
conflicts = 0
P2P = [0, 0, 0]
P2C = [0, 0, 0]
C2P = [0, 0, 0]
for key in IRR.keys():
    if key in IRR2.keys() and key in Ref.keys():
        if IRR2[key] == Ref[key] and IRR[key] == IRR[key]:
            correct += 1
        if IRR2[key] == Ref[key] and IRR[key] != IRR2[key] and IRR[key] != "P2P":
            notcorrect += 1
for key in Ref.keys():
    number_of_ASNs_in_ref_IRR = number_of_ASNs_in_ref_IRR + 1
for key in IRR.keys():
    number_of_ASNs_in_our_IRR = number_of_ASNs_in_our_IRR + 1
    if key in Ref.keys() and IRR[key] != "Unknown" and IRR[key] != "Conflict":
        knownkeysinboth += 1
    if key in Ref.keys() and IRR[key] == "Conflict":
        conflicts += 1
    if key in Ref.keys():
        number_of_ASNs_in_our_and_ref_IRR = number_of_ASNs_in_our_and_ref_IRR + 1
        if IRR[key] == Ref[key]:
            matching_classifications = matching_classifications + 1
            if IRR[key] == "P2P":
                P2P[0] += 1
            if IRR[key] == "P2C":
                P2C[1] += 1
            if IRR[key] == "C2P":
                C2P[2] += 1
        else:
            if Ref[key] == "P2P" and IRR[key] == "P2C":
                P2P[1] += 1
            if Ref[key] == "P2P" and IRR[key] == "C2P":
                P2P[2] += 1
            if Ref[key] == "P2C" and IRR[key] == "P2P":
                P2C[0] += 1
            if Ref[key] == "P2C" and IRR[key] == "C2P":
                P2C[2] += 1
            if Ref[key] == "C2P" and IRR[key] == "P2P":
                C2P[0] += 1
            if Ref[key] == "C2P" and IRR[key] == "P2C":
                C2P[1] += 1
confusion_matrix = [P2P, P2C, C2P]
#print(str(round(float(P2P[0])/(P2P[0] + P2P[1] + P2P[2]) * 100, 2)) + "%")
print(str(round(float(P2C[1])/(P2C[1] + P2C[2]) * 100, 2)) + "%")
print(str(round(float(C2P[2])/(C2P[1] + C2P[2]) * 100, 2)) + "%")
print(P2P)
print(P2C)
print(C2P)

print(str(round(float(matching_classifications)/knownkeysinboth * 100, 2)) + "%")
print("Number of Matching Classifications:", matching_classifications)
print("Number of ASNs in our_IRR:", number_of_ASNs_in_our_IRR)
print("Number of ASNs in our and Ref_IRR:", number_of_ASNs_in_our_and_ref_IRR)
print("Number of Known ASNs in our and Ref_IRR:", knownkeysinboth)
print("Number of ASNs in Ref IRR:", number_of_ASNs_in_ref_IRR)




with open('RefCompare.csv', mode='w', newline='') as f:
    fwrite = csv.writer(f, delimiter=',')
    fwrite.writerow(['AS1', 'AS2', 'IRR Prediction', 'Caida Prediction', ' '] * 50)
    w = []
    i = 0
    for k in Ref.keys():
        i = i + 1
        if k in IRR.keys():
            w = w + [k[0], k[1], IRR[k], Ref[k], ' ']
        else:
            w = w + [k[0], k[1], "Doesn't Exist", Ref[k], ' ']
        if i == 50:
            fwrite.writerow(w)
            w = []
            i = 0
    for k in (list(set(list(Ref.keys()) + list(IRR.keys())) - set(Ref.keys()))):
        i = i + 1
        w = w + [k[0], k[1], IRR[k], "Doesn't Exist", ' ']
        if i == 50:
            fwrite.writerow(w)
            w = []
            i = 0
    if i != 0:
        fwrite.writerow(w)



