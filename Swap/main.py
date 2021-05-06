import pickle
import time

with open("./../../Pickles/ASDict.pickle", "rb") as p:
    ASDict = pickle.load(p)
with open("./../../Pickles/Sets.pickle", "rb") as p:
    SetsDict = pickle.load(p)
with open("./../../Pickles/Names.pickle", "rb") as p:
    NamesDict = pickle.load(p)


def decipher_name(name, namelist):
    global MemDict, SetsDict, NamesDict
    retval = list()
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
                newretval = decipher_name(v, namelist)
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


def swap_entry(AS_list, origin, k, v, exp=False):
    global MemDict, ASDict
    if AS_list == [] or (len(AS_list) == 1 and AS_list[0] == origin): return
    for AS in AS_list:
        if AS in ASDict[k][exp].keys():
            if ASDict[k][exp][AS] == 'A': continue

            if v[origin] == 'A':
                ASDict[k][exp][AS] = v[origin]
                continue
            ASDict[k][exp][AS] = list() if ASDict[k][exp][AS] == 'Error' else ASDict[k][exp][AS]
            ASDict[k][exp][AS] = list(set(ASDict[k][exp][AS] + v[origin]))
        else:
            ASDict[k][exp][AS] = v[origin]
    del ASDict[k][exp][origin]


MemDict = dict()
st = time.time()
for k, v in ASDict.items():
    print(time.time() - st)
    imp_dict_copy = v[0].copy()
    exp_dict_copy = v[1].copy()
    for AS in imp_dict_copy.keys():
        AS_list = decipher_name(AS, [])
        swap_entry(AS_list, AS, k, imp_dict_copy)

    for AS in exp_dict_copy.keys():
        AS_list = decipher_name(AS, [])
        swap_entry(AS_list, AS, k, exp_dict_copy, exp=True)


with open("./../../Pickles/ASDictv2.pickle", "wb") as p:
    pickle.dump(ASDict, p)
with open("./../../Pickles/Mem.pickle", "wb") as p:
    pickle.dump(MemDict, p)
with open("./../../MemDict.txt", "w") as f:
    for k, v in MemDict.items():
        f.write(str(k) + ": " + str(v) + "\n")

