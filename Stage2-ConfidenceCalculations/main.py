import pickle
import codecs
import re
import time
from os import path
from math import *

st = time.time()
path = path.abspath(path.dirname(__file__))

with open(path + "\..\Pickles\IRR.pickle", "rb") as p:
    IRR1 = pickle.load(p)
with open(path + "\..\Pickles\IRRv2.pickle", "rb") as p:
    IRR2 = pickle.load(p)
with open(path + "\..\Pickles\IRRv3.pickle", "rb") as p:
    IRR3 = pickle.load(p)

IRR = {}


def conf_calc(class_list):
    num_of_1s = (0.5 * class_list[0:2].count(1) + 2 * class_list[2:].count(1)) / 9.0 * 6
    num_of_2s = (0.5 * class_list[0:2].count(2) + 2 * class_list[2:].count(2)) / 9.0 * 6
    num_of_3s = (0.5 * class_list[0:2].count(3) + 2 * class_list[2:].count(3)) / 9.0 * 6
    if num_of_1s > num_of_2s and num_of_1s > num_of_3s:
        x = num_of_1s
        dampen = ((num_of_2s ** 2) + (num_of_3s ** 2)) ** 0.5
        choice = 'P2P'
    elif num_of_2s > num_of_1s and num_of_2s > num_of_3s:
        x = num_of_2s
        dampen = ((num_of_1s ** 2) + (num_of_3s ** 2)) ** 0.5
        choice = 'P2C'
    else:
        x = num_of_3s
        dampen = ((num_of_1s ** 2) + (num_of_2s ** 2)) ** 0.5
        choice = 'C2P'
    a = 3 - dampen
    b = 1/3 + dampen
    const = 0.5 * (1 - (1/3) * dampen)
    result = 1.019075 * (1 - exp(-5 * x)) * ((1/pi) * atan(a * (x - b)) + const)
    return choice, max(0, min(result, 1))


def variable_extraction(AS1, AS2, dict_list):
    key = (AS1, AS2)
    revkey = (AS2, AS1)
    class_list = []
    for i in range(3):
        class_list.append(element_extraction(key, dict_list[i]))
        class_list.append(element_extraction(revkey, dict_list[i]))
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


for key in list(set(list(IRR1.keys()) + list(IRR2.keys()) + list(IRR3.keys()))):
    class_list = variable_extraction(key[0], key[1], [IRR1, IRR2, IRR3])  # [1, 1, 0, 0, 0, 0]
    IRR[key] = list(conf_calc(class_list)) + [class_list]

print(IRR)

with open(path + "/../Pickles/IRR_Confidence.pickle", "wb") as p:
    pickle.dump(IRR, p)








