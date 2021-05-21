import pickle
import multiprocessing as mp
from datetime import datetime

names = [
    'Sets',
    'Remarks',
    'I_E',
]

forbidden_offset = 5
two_sided_offset_100 = 0
with open("./../../Pickles/IRR.pickle", "rb") as p:
    IRR1 = pickle.load(p)
with open("./../../Pickles/IRRv2.pickle", "rb") as p:
    IRR2 = pickle.load(p)
with open("./../../Pickles/IRRv3.pickle", "rb") as p:
    IRR3 = pickle.load(p)


def Filter_All_Forbidden_ToRs(unfiltered_dict, mistake_threshold, two_sided_thresh_to_filter, name):
    global IRR1, IRR2, IRR3, forbidden_offset, two_sided_offset_100
    with open(f'./../../Pickles/Mistakes/{name} Dictionary/Mistake Threshold is {mistake_threshold}_.pickle', 'rb') as p:
        results = pickle.load(p)
    with open(f'./../../Pickles/2-Sides Requirement/{name} Dictionary/Requirement of at least '
              f'{two_sided_thresh_to_filter} 2-Sided ToRs.pickle', 'rb') as p:
        results2 = pickle.load(p)
    full_forbidden_set = set().union(results[two_sided_offset_100][forbidden_offset],results2[two_sided_offset_100][forbidden_offset])
    for arc in full_forbidden_set:
        if not isinstance(arc, tuple): continue
        del unfiltered_dict[arc]


two_sided_thresh_to_filter = 0
mistake_threshold = 0
IRR_Total = {'Remarks': IRR2, 'I/E': IRR1, 'Sets': IRR3}
print(len(IRR1.keys()))
for name in names:
    Filter_All_Forbidden_ToRs(IRR_Total[name], mistake_threshold, two_sided_thresh_to_filter, name)
    with open(f'./../../Pickles/Filtered/{name} Dictionary.pickle', 'wb') as p:
        pickle.dump(IRR_Total[name], p)
print(len(IRR1.keys()))