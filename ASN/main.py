import pickle
import codecs
from os import path

path = path.abspath(path.dirname(__file__))
ASName = {}


f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../Sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
for file in f:
    if file is not None:
        for block in file.read().split("\n\n"):
            block = block + "\n"
            if block.startswith("aut-num:"):
                key = "AS" + (block.lower().split("as")[1]).split("\n")[0]
                if '#' in key:
                    key = key.split('#')[0]
                if "as-name:" in block:
                    Name = block.split("as-name:")[1].split("\n")[0].strip()
                    if '#' in Name:
                        Name = Name.split('#')[0]
                    if Name.lower() != "unspecified":
                        ASName[Name] = key


print(ASName)

# with open(path + "/../Pickles/Names.pickle", "wb") as p:
#     pickle.dump(ASName, p)


