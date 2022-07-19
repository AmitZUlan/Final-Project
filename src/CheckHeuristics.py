import pickle
import time


with open("../Pickles/IRR.pickle", "rb") as p:
    IRR = pickle.load(p)
with open("../Pickles/IRRAA.pickle", "rb") as p:
    IRRAA = pickle.load(p)

ToR_count = 0
ToR_count2 = 0
correct = 0
correct_if_rev_not_in_keys = 0
for key in IRRAA.keys():
    if key[::-1] not in IRR.keys(): continue
    ToR_count += 1
    correct += IRRAA[key][::-1] == IRR[key[::-1]]
    if key[::-1] in IRRAA.keys(): continue
    ToR_count2 += 1
    correct_if_rev_not_in_keys += IRRAA[key][::-1] == IRR[key[::-1]]

print(correct)
print(correct_if_rev_not_in_keys)
print(ToR_count)
print(round(correct/ToR_count, 2))
print(round(correct_if_rev_not_in_keys/ToR_count2, 2))
