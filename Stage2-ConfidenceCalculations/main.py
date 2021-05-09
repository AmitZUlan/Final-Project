import pickle
import time
import csv
from matplotlib import pyplot as plt

st = time.time()
rev_class = {0: 0, 1: 1, 2: 3, 3: 2}

with open("./../../Pickles/IRR.pickle", "rb") as p:
    IRR1 = pickle.load(p)
with open("./../../Pickles/IRRv2.pickle", "rb") as p:
    IRR2 = pickle.load(p)
with open("./../../Pickles/IRRv3.pickle", "rb") as p:
    IRR3 = pickle.load(p)

IRR = dict()
IRR_class_only = dict()


def class_calc(class_list, _class):
    number = class_list[0:2].count(_class) + 0.5 * class_list[0:2].count(0)\
             + 2 * class_list[2:].count(_class) + class_list[2:].count(0)
    for i in range(3):
        if class_list[i] == _class and class_list[i + 1] == _class:
            number += 1
    return number


def conf_calc(class_list):
    if class_list == [0, 0, 0, 0, 0, 0]:
        return "Unknown", 0
    num_of_1s = class_calc(class_list, 1)
    num_of_2s = class_calc(class_list, 2)
    num_of_3s = class_calc(class_list, 3)
    if num_of_1s > num_of_2s and num_of_1s > num_of_3s:
        return 'P2P', num_of_1s / 13
    elif num_of_2s > num_of_1s and num_of_2s > num_of_3s:
        return 'P2C', num_of_2s / 13
    else:
        return 'C2P', num_of_3s / 13


def variable_extraction(AS1, AS2, dict_list):
    key = (AS1, AS2)
    revkey = (AS2, AS1)
    class_list = list()
    for i in range(3):
        class_list.append(element_extraction(key, dict_list[i]))
        class_list.append(rev_class[element_extraction(revkey, dict_list[i])])
    return class_list


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


count0 = 0
count1 = 0
count2 = 0
count90 = 0
count80 = 0
count70 = 0
count60 = 0
count50 = 0
count00 = 0

dict_list = [IRR1, IRR2, IRR3]
y = [variable_extraction(AS1, AS2, dict_list) for AS1, AS2 in list(set(list(IRR1.keys()) + list(IRR2.keys()) + list(IRR3.keys())))]
y = [6 - i.count(0) for i in y]
y = [y.count(i) for i in range(7)]
x = range(7)
plt.scatter(x, y)
plt.xlabel('# of Classifications')
plt.ylabel('# of ToRs with x Classifications')
for xi, yi in zip(x, y):
    label = f"({xi}, {yi})"
    plt.annotate(label,
                 (xi, yi),
                 textcoords="offset points",
                 xytext=(0, 10),
                 ha='center')
plt.show()


for key in list(set(list(IRR1.keys()) + list(IRR2.keys()) + list(IRR3.keys()))):
    class_list = variable_extraction(key[0], key[1], [IRR1, IRR2, IRR3])  # [1, 1, 0, 0, 0, 0]
    value = list(conf_calc(class_list))
    IRR[key] = value + [class_list]
    IRR_class_only[key] = value[0]
    if class_list.count(0) == 0:
        count0 += 1
        variable_extraction(key[0], key[1], [IRR1, IRR2, IRR3])
        list(conf_calc(class_list))
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
    fwrite.writerow(['AS1', 'AS2', 'Imp/Exp[AS1, AS2]', 'Imp/Exp[AS2, AS1]',
                     'Remarks[AS1, AS2]', 'Remarks[AS2, AS1]', 'Sets[AS1, AS2]',
                     'Sets[AS2, AS1]', 'ToR', 'Confidence'])
    for k in IRR.keys():
        w = [k[0][2:], k[1][2:]] + IRR[k][2] + [IRR[k][0], IRR[k][1], ' ']
        fwrite.writerow(w)









