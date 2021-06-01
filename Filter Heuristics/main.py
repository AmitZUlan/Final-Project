import pickle


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


def filter_all_forbidden_ToRs(unfiltered_dict, mistake_threshold, two_sided_thresh_to_filter, name):
    global IRR1, IRR2, IRR3, forbidden_offset, two_sided_offset_100
    with open(f'./../../Pickles/Mistakes/{name} Dictionary/Mistake Threshold is {mistake_threshold}%.pickle', 'rb') as p:
        results = pickle.load(p)
    with open(f'./../../Pickles/2-Sides Requirement/{name} Dictionary/Requirement of at least '
              f'{two_sided_thresh_to_filter} 2-Sided ToRs.pickle', 'rb') as p:
        results2 = pickle.load(p)
    full_forbidden_set = set().union(results[two_sided_offset_100][forbidden_offset], results2[two_sided_offset_100][forbidden_offset])
    unknowns = {arc for arc, val in unfiltered_dict.items() if val == 'Unknown'}
    for arc in full_forbidden_set.union(unknowns):
        if not isinstance(arc, tuple): continue
        del unfiltered_dict[arc]


def force_2_sided(given_IRR, mistakes, classifications_2_sided, rev_relevant_dict=None):
    IRR_dup = dict()
    for key, value in given_IRR.items():
        IRR_dup[key] = value
        if key[::-1] not in given_IRR.keys():
            IRR_dup[key[::-1]] = given_IRR[key][::-1]
        else:
            if given_IRR[key] == given_IRR[key[::-1]][::-1]:
                IRR_dup[key[::-1]] = given_IRR[key][::-1]
                continue
            key0 = rev_relevant_dict[key] if rev_relevant_dict else key[0]
            key1 = rev_relevant_dict[key[::-1]] if rev_relevant_dict else key[1]
            confidence0 = 1 - len(mistakes.get(key0, set())) / len(classifications_2_sided[key0])
            confidence1 = 1 - len(mistakes.get(key1, set())) / len(classifications_2_sided[key1])
            if confidence0 > confidence1:
                IRR_dup[key[::-1]] = given_IRR[key][::-1]
            else:
                if confidence0 != confidence1:
                    IRR_dup[key] = given_IRR[key[::-1]][::-1]
                    IRR_dup[key[::-1]] = given_IRR[key[::-1]]
                else:
                    if len(classifications_2_sided[key0]) > len(classifications_2_sided[key1]):
                        IRR_dup[key[::-1]] = given_IRR[key][::-1]
                    else:
                        IRR_dup[key] = given_IRR[key[::-1]][::-1]
                        IRR_dup[key[::-1]] = given_IRR[key[::-1]]
    return IRR_dup


two_sided_thresholds = (3, 3, 5)
agreements_thresholds = (90, 80, 80)
IRR_Total = {'Sets': IRR3, 'Remarks': IRR2, 'I_E': IRR1}
for name, agreements_threshold, two_sided_threshold in zip(names, agreements_thresholds, two_sided_thresholds):
    with open(f'./../../Pickles/Mistakes/{name} Dictionary Mistakes.pickle', 'rb') as p:
        mistakes = pickle.load(p)
    with open(f'./../../Pickles/Classifications/{name} Dictionary Classifications 2-Sided.pickle', 'rb') as p:
        classifications_2_sided = pickle.load(p)
    if name != 'I_E':
        with open(f"./../../Pickles/rev {name} Relevant to {name} Heuristic.pickle", "rb") as p:
            rev_relevant_dict = pickle.load(p)
    else:
        rev_relevant_dict = None
    print(f'{name}: Initial Number of keys - {len(IRR_Total[name].keys())}')
    filter_all_forbidden_ToRs(IRR_Total[name], 100 - agreements_threshold, two_sided_threshold, name)
    print(f'{name}: Number of keys after Filtering - {len(IRR_Total[name].keys())}')
    IRR_Total[name] = force_2_sided(IRR_Total[name], mistakes, classifications_2_sided, rev_relevant_dict)
    print(f'{name}: Final Number of keys - {len(IRR_Total[name].keys())}')
    with open(f'./../../Pickles/Filtered/{name} Dictionary.pickle', 'wb') as p:
        pickle.dump(IRR_Total[name], p)
