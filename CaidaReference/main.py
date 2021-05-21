import pickle
import codecs
import re
import time
from os import path

path = path.abspath(path.dirname(__file__))
with open("CaidaReference.txt", 'r') as f:
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

with open(path + "/../Pickles/Ref.pickle", "wb") as p:
    pickle.dump(Ref, p)
with open(path + "/../Example Files/RefDict.txt", "w") as f:
    for k, v in Ref.items():
        f.write(str(k) + ": " + str(v) + "\n")