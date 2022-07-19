import pickle
import time

with open(f"../Pickles/ASDict.pickle", "rb") as p:
    ASDict = pickle.load(p)
with open(f"../Pickles/Sets.pickle", "rb") as p:
    SetsDict = pickle.load(p)
with open(f"../Pickles/Names.pickle", "rb") as p:
    NamesDict = pickle.load(p)
MemDict = dict()


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


def swap_entry(AS_list, origin, k, v, exp=False):
    global MemDict, ASDict
    if AS_list == set() or AS_list == {origin}: return
    for AS in AS_list:
        if AS in ASDict[k][exp].keys():
            if ASDict[k][exp][AS] == 'A': continue

            if v[origin] == 'A':
                ASDict[k][exp][AS] = 'A'
                continue
            ASDict[k][exp][AS] = set() if ASDict[k][exp][AS] == 'Error' else ASDict[k][exp][AS]
            ASDict[k][exp][AS].update(v[origin])
        else:
            ASDict[k][exp][AS] = v[origin]
    del ASDict[k][exp][origin]


def main():
    st = time.time()
    for k, v in ASDict.items():
        print(time.time() - st)

        imp_dict_copy = v[0].copy()
        for AS in imp_dict_copy.keys():
            AS_list = decipher_name(AS, set())
            swap_entry(AS_list, AS, k, imp_dict_copy)

        exp_dict_copy = v[1].copy()
        for AS in exp_dict_copy.keys():
            AS_list = decipher_name(AS, set())
            swap_entry(AS_list, AS, k, exp_dict_copy, exp=True)

    with open("../Pickles/ASDictv2.pickle", "wb") as p:
        pickle.dump(ASDict, p)
    with open("../Pickles/Mem.pickle", "wb") as p:
        pickle.dump(MemDict, p)
    with open("../MemDict.txt", "w") as f:
        for k, v in MemDict.items():
            f.write(str(k) + ": " + str(v) + "\n")

