import pickle
import time


st = time.time()
with open("./../../Pickles/ASDictv2.pickle", "rb") as p:
    ASDict = pickle.load(p)

not_numeric = 0
ASNum = len(ASDict.keys())
IRR = dict()
for AS1, (imp_dict, exp_dict) in ASDict.items():
    print(time.time() - st)
    for AS2 in imp_dict.keys():
        if AS1 == AS2:
            continue
        if not AS1.startswith("AS") or not AS1[2:].isnumeric():
            not_numeric += 1
            continue
        if not AS2.startswith("AS") or not AS2[2:].isnumeric():
            not_numeric += 1
            continue
        key = (AS1, AS2)
        if AS2 not in exp_dict.keys() or imp_dict[AS2] == "Error" or exp_dict[AS2] == "Error":
            IRR[key] = "Unknown"
        elif imp_dict[AS2] == 'A' and exp_dict[AS2] == 'A':
            condition = list(ASDict[AS1][1].values()).count('A') > list(ASDict.get(AS2, [{}, {}])[1].values()).count('A')
            IRR[key] = 'P2C' if condition else 'C2P'
        elif imp_dict[AS2] == 'A':
            IRR[key] = "C2P"
        elif exp_dict[AS2] == 'A':
            IRR[key] = "P2C"
        elif imp_dict[AS2] != 'A' and exp_dict[AS2] != 'A':
            IRR[key] = "P2P"

    for AS2 in exp_dict.keys():
        key = (AS1, AS2)
        if AS2 not in imp_dict.keys():
            IRR[key] = "Unknown"


print(IRR)
print(not_numeric)
print(ASNum)
print(len(list(IRR.keys())))

with open("./../../Pickles/IRR.pickle", "wb") as p:
    pickle.dump(IRR, p)
with open("./../../Example Files/IRRDict.txt", "w") as f:
    for k, v in IRR.items():
        f.write(str(k) + ": " + str(v) + "\n")
