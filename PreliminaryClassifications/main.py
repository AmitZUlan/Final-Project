import pickle
import time

st = time.time()
with open("./../../Pickles/ASDictv2.pickle", "rb") as p:
    ASDict = pickle.load(p)


def calc_P2C(AS, depth, check_exceeded):
    global P2C_dict, P2C_memo
    exceeded = False
    if depth > 950:
        return 1, True
    if AS in P2C_memo.keys() and (not check_exceeded or not P2C_memo[AS][1]):
        return P2C_memo[AS]
    if AS not in P2C_dict.keys():
        P2C_memo[AS] = 0, False
        return 0, False
    P2C_count = 0
    for AS2 in P2C_dict[AS]:
        temp, btemp = calc_P2C(AS2, depth + 1, check_exceeded)
        P2C_count += 1 + temp
        exceeded |= btemp
    P2C_memo[AS] = (P2C_count, exceeded)
    return P2C_count, exceeded


count = 0
not_numeric = 0
ASNum = len(ASDict.keys())
IRR = dict()
P2C_dict = dict()
P2C_memo = dict()
IRRAA = dict()
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
        elif imp_dict[AS2] == 'A' and exp_dict[AS2] == 'A': continue
            # condition = list(ASDict[AS1][1].values()).count('A') > list(ASDict.get(AS2, ({}, {}))[1].values()).count('A')
            # IRR[key] = 'P2C' if condition else 'C2P'
            # IRRAA[key] = 'P2C' if condition else 'C2P'
        elif imp_dict[AS2] == 'A':
            IRR[key] = "C2P"
        elif exp_dict[AS2] == 'A':
            IRR[key] = "P2C"
            P2C_dict[AS1] = P2C_dict.get(AS1, set())
            P2C_dict[AS1].add(AS2)
        elif imp_dict[AS2] != 'A' and exp_dict[AS2] != 'A':
            IRR[key] = "P2P"

    for AS2 in exp_dict.keys():
        key = (AS1, AS2)
        if AS2 not in imp_dict.keys():
            IRR[key] = "Unknown"
for i in range(1):
    for AS1, (imp_dict, exp_dict) in ASDict.items():
        print(time.time() - st)
        for AS2 in imp_dict.keys():
            if AS1 == AS2:
                continue
            if not AS1.startswith("AS") or not AS1[2:].isnumeric(): continue
            if not AS2.startswith("AS") or not AS2[2:].isnumeric(): continue
            key = (AS1, AS2)
            if AS2 not in exp_dict.keys() or imp_dict[AS2] == "Error" or exp_dict[AS2] == "Error": continue
            elif imp_dict[AS2] == 'A' and exp_dict[AS2] == 'A':
                IRR[key] = IRR.get(key[::-1], 'Unknown')[::-1] if IRR.get(key[::-1], 'Unknown') != 'Unknown' else IRR.get(key[::-1], 'Unknown')
                IRRAA[key] = IRR[key]
                if IRR[key] == 'Unknown':
                    condition = list(ASDict[AS1][1].values()).count('A') > list(ASDict.get(AS2, ({}, {}))[1].values()).count('A')
                    IRR[key] = 'P2C' if condition else 'C2P'
                    IRRAA[key] = 'P2C' if condition else 'C2P'


print(IRR)
print(not_numeric)
print(ASNum)
print(len(list(IRR.keys())))
print(count)

with open("./../../Pickles/IRR.pickle", "wb") as p:
    pickle.dump(IRR, p)
with open("./../../Pickles/IRRAA.pickle", "wb") as p:
    pickle.dump(IRRAA, p)
# with open("./../../Example Files/IRRDict.txt", "w") as f:
#     for k, v in IRR.items():
#         f.write(str(k) + ": " + str(v) + "\n")
