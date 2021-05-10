import pickle
import time

st = time.time()
IRR = dict()

with open("./../../Pickles/Mem.pickle", "rb") as p:
    MemDict = pickle.load(p)
with open("./../../Pickles/Sets.pickle", "rb") as p:
    SetsDict = pickle.load(p)
with open("./../../Pickles/Names.pickle", "rb") as p:
    NamesDict = pickle.load(p)

customers = ["customer", "custs", "downstream", "client", "downlink"]
providers = ["provider", "upstream", "uplink", "backbone"]


def decipher_name(name, namelist):
    global MemDict, SetsDict, NamesDict
    retval = set()
    if name in MemDict.keys():
        return MemDict[name]
    if name.startswith("AS") and name[2:].strip().isnumeric():
        retval.add(name.strip())
        MemDict[name] = retval
        return retval
    if name in namelist:
        assert retval == set()
        return retval
    if name in NamesDict.keys():
        retval.update(NamesDict[name])
    elif name.lower().startswith("as-") and name[3:].strip().isnumeric():
        retval.add('AS' + name[3:].strip())
        MemDict[name] = retval
        return retval
    elif SetsDict.get(name, set()) != set():
        for AS in SetsDict[name]:
            if AS != name:
                namelist.add(name)
                newretval = decipher_name(AS, namelist)
                namelist.remove(name)
                retval.update(newretval)
            else:
                SetsDict[name].remove(name)
    MemDict[name] = retval
    return retval


for name in SetsDict.keys():
    b1 = False
    b2 = False
    b3 = False
    AS2list = decipher_name(name, set())
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
        AS1list = decipher_name(AS1list, set())
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
    if '-backbone' in name.lower():
        AS1list = name[:name.lower().find("-backbone")]
        AS1list = decipher_name(AS1list, set())
        if not AS1list: continue
        for AS1 in AS1list:
            for AS2 in AS2list:
                if AS2 == AS1: continue
                key = (AS1, AS2)
                if AS1 in AS2list and AS2 in AS1list:
                    continue
                IRR[key] = "C2P"


print("P2P Value is:", list(IRR.values()).count("P2P"))
print("P2C Value is:", list(IRR.values()).count("P2C"))
print("C2P Value is:", list(IRR.values()).count("C2P"))

with open("./../../Pickles/IRRv3.pickle", "wb") as p:
    pickle.dump(IRR, p)
with open("./../../Pickles/Mem.pickle", "wb") as p:
    pickle.dump(MemDict, p)
