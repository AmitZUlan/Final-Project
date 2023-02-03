import time
import csv
import pickle

st = time.time()

with open(f"../Pickles/Problink.pickle", "rb") as p:
    Problink = pickle.load(p)

with open(f"../Pickles/RestoredSiblingsDict.pickle", "rb") as p:
    SiblingIRR = pickle.load(p)

comparison = [['AS1', 'AS2', 'Our ToR', 'Problink ToR']]
knownKeys = set()

for AS1, AS2 in set(SiblingIRR.keys()).intersection(set(Problink.keys())):
    key = (AS1, AS2)
    if SiblingIRR.get(key, ['Missing'])[0] != 'S2S' and Problink.get(key, 'Missing') != 'S2S': continue
    if key in knownKeys: continue
    knownKeys.add(key)
    row = [AS1[2:], AS2[2:], SiblingIRR.get(key, ['Missing'])[0], Problink.get(key, 'Missing')]
    comparison.append(row)

for AS1, AS2 in set().union(set(SiblingIRR.keys()), set(Problink.keys())):
    key = (AS1, AS2)
    if SiblingIRR.get(key, ['Missing'])[0] != 'S2S' and Problink.get(key, 'Missing') != 'S2S': continue
    if key in knownKeys: continue
    knownKeys.add(key)
    row = [AS1[2:], AS2[2:], SiblingIRR.get(key, ['Missing'])[0], Problink.get(key, 'Missing')]
    comparison.append(row)

t = time.time()
print(round(t - st, 2))

with open("../Example Files/Problink Siblings Comparison.csv", mode='w', newline='') as f:
    writer = csv.writer(f, dialect='excel')
    for row in comparison:
        writer.writerow(row)