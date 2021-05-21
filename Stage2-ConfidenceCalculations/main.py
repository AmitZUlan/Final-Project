import pickle
import time
import csv

st = time.time()
IRR = dict()
IRR_class_only = dict()
dict_list = list()
mistakes_list = list()
classifications_list = list()
num_to_class = {
    1: 'P2P',
    2: 'P2C',
    3: 'C2P',
}

with open("./../../Pickles/IRR.pickle", "rb") as p:
    IRR1 = pickle.load(p)
    dict_list.append(IRR1)
with open("./../../Pickles/IRRv2.pickle", "rb") as p:
    IRR2 = pickle.load(p)
    dict_list.append(IRR2)
with open("./../../Pickles/IRRv3.pickle", "rb") as p:
    IRR3 = pickle.load(p)
    dict_list.append(IRR3)

for arg in ['Sets Dictionary', 'Remarks Dictionary', 'I_E Dictionary']:
    with open(f'./../../Pickles/Mistakes/{arg} Mistakes.pickle', 'rb') as p:  # (AS1, AS2)
        mistakes = pickle.load(p)
        mistakes_list.append(mistakes)
    with open(f'./../../Pickles/Classifications/{arg} Classifications 2-Sided.pickle', 'rb') as p:
        classifications_2_sided = pickle.load(p)
        classifications_list.append(classifications_2_sided)


def is_match(key):
    global dict_list
    if dict_list[0].get(key, 'Unknown0') == dict_list[1].get(key, 'Unknown1'):
        return dict_list[0][key]
    if dict_list[1].get(key, 'Unknown1') == dict_list[2].get(key, 'Unknown2'):
        return dict_list[1][key]
    if dict_list[0].get(key, 'Unknown0') == dict_list[2].get(key, 'Unknown2'):
        return dict_list[2][key]
    return 'Unknown'


def variable_extraction(key, dict_list):
    class_list = list()
    for i in range(3):
        class_list.append(element_extraction(key, dict_list[i]))
    return tuple(class_list)


def element_extraction(key, dict):
    if key not in dict.keys():
        return 0
    else:
        if dict[key] == 'P2P':
            return 1
        elif dict[key] == 'P2C':
            return 2
        elif dict[key] == 'C2P':
            return 3
        else:
            return 0


def in_dict(dict_set, key):
    for dic in dict_set:
        if dic.get(key, 'Unknown') != 'Unknown':
            return False
    return True


def conf_calc(key, class_list):
    global mistakes_list, classifications_list
    if class_list == (0, 0, 0):
        return 'Unknown', 0
    ToR = is_match(key)
    if ToR != 'Unknown':
        return ToR, 1
    AS = key[0]
    confidence1 = 1 - len(mistakes_list[0].get(AS, {1})) / len(classifications_list[0].get(AS, {1})) if class_list[0] else 0
    confidence2 = 1 - len(mistakes_list[1].get(AS, {1})) / len(classifications_list[1].get(AS, {1})) if class_list[1] else 0
    confidence3 = 1 - len(mistakes_list[2].get(AS, {1})) / len(classifications_list[2].get(AS, {1})) if class_list[2] else 0
    assertion = confidence1 != 0 or confidence2 != 0 or confidence3 != 0
    if not assertion:
        for val in class_list:
            if val != 0:
                return num_to_class[val], 0
    conf_dict = dict()
    conf_dict[confidence1] = IRR1.get(key, 'Unknown')
    conf_dict[confidence2] = IRR2.get(key, 'Unknown')
    conf_dict[confidence3] = IRR3.get(key, 'Unknown')
    return conf_dict[max(confidence1, confidence2, confidence3)], max(confidence1, confidence2, confidence3)


count0 = 0
count1 = 0
count2 = 0
count90 = 0
count80 = 0
count70 = 0
count60 = 0
count50 = 0
count00 = 0


ToR_count = 0
percent = list(int(i * len(set().union(IRR1.keys(), IRR2.keys(), IRR3.keys()))/20) for i in range(1, 21))
percent.append(1)
percent.sort()
percent_set = set(percent)
for key in set().union(IRR1.keys(), IRR2.keys(), IRR3.keys()):
    ToR_count += 1
    if ToR_count in percent_set:
        print(f"{percent.index(ToR_count) * 5}%")
    class_list = variable_extraction(key, dict_list)
    value = conf_calc(key, class_list)
    IRR[key] = value
    IRR_class_only[key] = value[0]
    if value[0] != 'Unknown':
        if key[::-1] not in IRR or IRR[key[::-1]][1] < value[1]:
            IRR[key[::-1]] = (value[0][::-1], value[1])
            IRR_class_only[key[::-1]] = value[0][::-1]
    if class_list.count(0) == 0:
        count0 += 1
        variable_extraction(key, dict_list)
        print(key, IRR[key])
    if class_list.count(0) == 1:
        count1 += 1
    if class_list.count(0) == 2:
        count2 += 1
    if IRR[key][1] > 0.9:
        count90 += 1
    if IRR[key][1] > 0.8:
        count80 += 1
    if IRR[key][1] > 0.7:
        count70 += 1
    if IRR[key][1] > 0.6:
        count60 += 1
    if IRR[key][1] >= 0.5:
        count50 += 1
    if IRR[key][1] < 0.5:
        count00 += 1
# print(IRR)
print("number of full class_lists is:", count0)
print("number of missing 1 classification class_lists is:", count1)
print("number of missing 2 classification class_lists is:", count2)
print("number of ToRs above 90% confidence is:", count90)
print("number of ToRs above 80% confidence is:", count80)
print("number of ToRs above 70% confidence is:", count70)
print("number of ToRs above 60% confidence is:", count60)
print("number of ToRs above 50% confidence is:", count50)
print("number of ToRs below 50% confidence is:", count00)

with open("./../../Pickles/IRR_Confidence.pickle", "wb") as p:
    pickle.dump(IRR, p)
with open("./../../Pickles/IRR_Confidence_class_only.pickle", "wb") as p:
    pickle.dump(IRR_class_only, p)

with open("./../../Example Files/IRR.csv", mode='w', newline='') as f:
    fwrite = csv.writer(f, delimiter=',')
    fwrite.writerow(['AS1', 'AS2', 'ToR', 'Confidence'])
    for k in IRR.keys():
        fwrite.writerow([k[0][2:], k[1][2:], IRR[k][0], IRR[k][1]])









