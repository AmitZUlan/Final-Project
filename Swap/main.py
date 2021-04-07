import pickle
import codecs
import re
import time
from os import path

path = path.abspath(path.dirname(__file__))

with open(path + "\..\Pickles\ASDict.pickle", "rb") as p:
    ASDict = pickle.load(p)
with open(path + "\..\Pickles\Sets.pickle", "rb") as p:
    SetsDict = pickle.load(p)
with open(path + "\..\Pickles\\Names.pickle", "rb") as p:
    NamesDict = pickle.load(p)


def decipher_name(NamesDict, SetsDict, name, count, MemDict, namelist):
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
                newretval = decipher_name(NamesDict, SetsDict, v, count + 1, MemDict, namelist)
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


def swap_entry(AS_list, origin, k, impexp, v):
    global MemDict
    global ASDict
    if AS_list != [] and AS_list[0] != origin:
        for AS in AS_list:
            if AS in ASDict[k][impexp].keys():
                if ASDict[k][impexp][AS] != 'A':
                    if v[origin] == 'A':
                        ASDict[k][impexp][AS] = v[origin]
                    if ASDict[k][impexp][AS] == "Error":
                        ASDict[k][impexp][AS] = []
                    ASDict[k][impexp][AS] = list(set(ASDict[k][impexp][AS] + v[origin]))
            else:
                ASDict[k][impexp][AS] = v[origin]
        del ASDict[k][impexp][origin]


MemDict = {}
st = time.time()
i = 0
for k, v in ASDict.items():
    print(time.time() - st)
    for AS in (v[0].copy()).keys():
        AS_list = decipher_name(NamesDict, SetsDict, AS, 0, MemDict, [])
        swap_entry(AS_list, AS, k, 0, v[0].copy())

    for AS in (v[1].copy()).keys():
        AS_list = decipher_name(NamesDict, SetsDict, AS, 0, MemDict, [])
        swap_entry(AS_list, AS, k, 1, v[1].copy())


print(ASDict)


with open(path + "/../Pickles/ASDictv2_temp.pickle", "wb") as p:
    pickle.dump(ASDict, p)
with open(path + "/../Pickles/Mem.pickle", "wb") as p:
    pickle.dump(MemDict, p)
with open(path + "/../MemDict.txt", "w") as f:
    for k, v in MemDict.items():
        f.write(str(k) + ": " + str(v) + "\n")
# with open("UpgradedImp.pickle", "rb") as p:
#     DictImp = pickle.load(p)
# with open("UpgradedExp.pickle", "rb") as p:
#     DictExp = pickle.load(p)
# for k, v in DictImp.items():
#     for val in v:
#         if not val[0].split("AS")[1].isnumeric():
#             print(1)
# for k, v in DictExp.items():
#     for val in v:
#         if not val[0].split("AS")[1].isnumeric():
#             print(1)
