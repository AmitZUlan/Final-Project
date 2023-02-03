import pickle
import codecs
import re
import time
from os import path


path = path.abspath(path.dirname(__file__))
with open("./CaidaReferences/CaidaReference.txt", 'r') as f:
    Ref = dict()
    file = f.read()
for line in file.split("\n"):
    if line == '' or line[0] == '#':
        continue
    line = line.split("|")
    Rel = ("AS" + line[0], "AS" + line[1])
    RelRev = ("AS" + line[1], "AS" + line[0])
    if line[2] == '0':
        Ref[Rel] = "P2P"
        Ref[RelRev] = "P2P"
    elif line[2] == '-1':
        Ref[Rel] = "P2C"
        Ref[RelRev] = "C2P"
    else:
        assert False
print(Ref)
print(len(list(Ref.keys())))

with open("../Pickles/Ref.pickle", "wb") as p:
    pickle.dump(Ref, p)
with open("../Example Files/RefDict.txt", "w") as f:
    for k, v in Ref.items():
        f.write(str(k) + ": " + str(v) + "\n")


# read Problink.txt
with open('./CaidaReferences/ProbLink-dataset.txt') as f:
    file = f.read()

probLink = dict()
tor = {'-1': 'P2C', '0': 'P2P', '1': 'S2S'}
# convert to dictionary
for line in file.split('\n'):
    if line == '' or line[0] == '#': continue
    line = line.split('#')[0]
    inference = line.split('|')
    probLink[f'AS{inference[0]}', f'AS{inference[1]}'] = tor[inference[2]]
    probLink[f'AS{inference[1]}', f'AS{inference[0]}'] = tor[inference[2]][::-1]

print(probLink)
print((len(probLink.keys())))
with open("../Pickles/Problink.pickle", "wb") as p:
    pickle.dump(probLink, p)
