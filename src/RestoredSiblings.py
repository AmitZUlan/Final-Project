import pickle
import csv
import time


st = time.time()
ASSiblings = dict()
AS_Siblings = dict()
SiblingIRR: dict = dict()


def analyze_row(row):
    global ASSiblings
    fields = list(f.strip().split('=')[0] for f in row[3].split(','))
    values = list(f.strip().split('=')[1] for f in row[3].split(','))
    for field, value in zip(fields, values):
        ASSiblings[field] = ASSiblings.get(field, dict())
        ASSiblings[field][value] = ASSiblings.get(field, dict()).get(value, set()).union({f'AS{row[0]}', f'AS{row[1]}'})


def sibling_insertion(source_dict, field, forbidden_list={'dum', 'yahoo', 'aol.com', 'hotmail', 'live.com', 'outlook.com', 'gmail', 'unspecified'}, max_len=10**9):
    global AS_Siblings
    for key in source_dict.keys():
        if len(source_dict[key]) < 2 or max_len < len(source_dict[key])\
                or any([word in key.lower() for word in forbidden_list]):
            continue
        for AS in source_dict[key]:
            AS_Siblings[AS] = AS_Siblings.get(AS, dict())
            siblings_list = source_dict[key].copy()
            siblings_list.remove(AS)
            AS_Siblings[AS][f"{field}={key}"] = siblings_list


def concat_siblings(AS_Siblings):
    global SiblingIRR
    for AS, sibling_indicator in AS_Siblings.items():
        sibling_set = set()
        sibling_set.update(*sibling_indicator.values())
        for sibling in sibling_set:
            comment = [indicator for indicator in sibling_indicator.keys() if sibling in sibling_indicator[indicator]]
            comment = ', '.join(comment)
            SiblingIRR[(AS, sibling)] = ('S2S', comment)


with open('../Siblings Threshold=5.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile)
    firstLine = True
    for row in spamreader:
        if firstLine:
            firstLine = False
            continue
        # SiblingIRR[(f'AS{row[0]}', f'AS{row[1]}')] = row[2]
        analyze_row(row)

print(ASSiblings)
t = time.time()
print(round(t - st, 2))

for k, v in ASSiblings.items():
    sibling_insertion(v, k, max_len=5)


concat_siblings(AS_Siblings)
t = time.time()
print(round(t - st, 2))
print(SiblingIRR)

with open('../Pickles/RestoredSiblingsDict.pickle', 'wb') as f:
    pickle.dump(SiblingIRR, f)


# t = time.time()
# print(round(t - st, 2))
#
# comparison = [['AS1', 'AS2', 'Our ToR', 'Problink ToR']]
# knownKeys = set()
#
# for AS1, AS2 in set(SiblingIRR.keys()).intersection(set(Problink.keys())):
#     key = (AS1, AS2)
#     if key in knownKeys: continue
#     knownKeys.add(key)
#     row = [AS1[2:], AS2[2:], SiblingIRR.get(key, 'Missing'), Problink.get(key, 'Missing')]
#     comparison.append(row)
#
# for AS1, AS2 in set().union(set(SiblingIRR.keys()), set(Problink.keys())):
#     key = (AS1, AS2)
#     if key in knownKeys: continue
#     knownKeys.add(key)
#     row = [AS1[2:], AS2[2:], SiblingIRR.get(key, 'Missing'), Problink.get(key, 'Missing')]
#     comparison.append(row)
#
# t = time.time()
# print(round(t - st, 2))
#
# with open("../Example Files/Problink Siblings Comparison.csv", mode='w', newline='') as f:
#     writer = csv.writer(f, dialect='excel')
#     for row in comparison:
#         writer.writerow(row)

