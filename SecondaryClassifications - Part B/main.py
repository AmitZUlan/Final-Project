import pickle
import codecs
import re
import time
from os import path

st = time.time()
path = path.abspath(path.dirname(__file__))
IRR = {}

with open(path + "\..\Pickles\Mem.pickle", "rb") as p:
    MemDict = pickle.load(p)
with open(path + "\..\Pickles\Sets.pickle", "rb") as p:
    SetsDict = pickle.load(p)
with open(path + "\..\Pickles\\Names.pickle", "rb") as p:
    NamesDict = pickle.load(p)

customers = ["customer", "custs", "downstream", "client", "downlink"]
providers = ["provider", "upstream", "uplink"]


def swap(NamesDict, SetsDict, name, MemDict, namelist):
    retval = []
    if name in MemDict.keys():
        return MemDict[name]
    if name.startswith("AS") and name[2:].isnumeric():
        retval.append(name)
        MemDict[name] = retval
        return retval
    if name in namelist:
        return []
    if name in NamesDict.keys():
        retval.append(NamesDict[name])
    elif name in SetsDict.keys():
        for v in SetsDict[name]:
            if v != name:
                namelist.append(name)
                newretval = swap(NamesDict, SetsDict, v, MemDict, namelist)
                namelist.remove(name)
                retval = list(set(retval + newretval))
            else:
                SetsDict[name].remove(name)
    elif name.startswith("AS") and name[2] == '-' and name[3:].isnumeric():
        retval.append(name[:2] + name[3:])
        MemDict[name] = retval
        return retval
    else:
        for key, v in NamesDict.items():
            if ':' not in name and (len(name) > 2 and name in key or (name.startswith("AS") and name[2:] in key and name.lower()[2:] not in "as" and name.lower()[2:] not in "asn" and len(name) > 4) or (name.startswith("AS-") and name[3:] in key and name.lower()[3:] not in "as" and name.lower()[3:] not in "asn" and len(name) > 5)):
                retval.append(v)
            MemDict[name] = retval
            return retval
        retval.append(name)
    MemDict[name] = retval
    return retval


for name in SetsDict.keys():
    b1 = False
    b2 = False
    b3 = False
    AS2list = swap(NamesDict, SetsDict, name, MemDict, [])
    if ':' in name:
        if "peer" in name.lower():
            b1 = True
        if name.lower().split(":")[1] == "as-p":
            b1 = True
        for word in providers:
            if word in name.lower():
                b2 = True
                break
        for word in customers:
            if word in name.lower():
                b3 = True
                break
        AS1list = name.split(':')[0]
        AS1list = swap(NamesDict, SetsDict, AS1list, MemDict, [])
        if not AS1list:
            continue
        else:
            if not b1 and not b2 and not b3:
                continue
            if (b1 and b2) or (b2 and b3) or (b1 and b3):
                continue
            for AS1 in AS1list:
                for AS2 in AS2list:
                    if AS2 != AS1:
                        key = (AS1, AS2)
                        revkey = (AS2, AS1)
                        if AS1 in AS2list and AS2 in AS1list:
                            continue
                        if b1 and not b2 and not b3:
                            IRR[key] = "P2P"
                            continue
                        if not b1 and b2 and not b3:
                            IRR[key] = "C2P"
                            continue
                        if not b1 and not b2 and b3:
                            IRR[key] = "P2C"
                            continue


with open(path + "/../Pickles/IRRv3.pickle", "wb") as p:
    pickle.dump(IRR, p)
with open(path + "/../Pickles/Mem.pickle", "wb") as p:
    pickle.dump(MemDict, p)
