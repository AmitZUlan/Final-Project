import pickle
import multiprocessing as mp

if __name__ == '__main__':
    with open("../Pickles/Remarks Relevant to Remarks Heuristic.pickle", "rb") as p:
        relevant_remarks = pickle.load(p)
    with open("../Pickles/Sets Relevant to Sets Heuristic.pickle", "rb") as p:
        relevant_sets = pickle.load(p)
    with open("../Pickles/IRR.pickle", "rb") as p:
        I_E_dict = pickle.load(p)


def key_analysis(given_dicts, key1):
    dict1, dict2 = given_dicts
    key2 = key1[::-1]
    if dict1.get(key1, 'Unknown') == 'Unknown' or dict2.get(key2, 'Unknown') == 'Unknown':
        return 0, 0
    val1 = dict1[key1]
    val2 = dict2[key2][::-1]
    return 1, val1 == val2


def add_key_to_set(dic, key, arc, condition=True):
    if not condition: return
    dic[key] = dic.get(key, set())
    dic[key].add(arc)


def secondary_heuristic_analysis(given_IRR, I_E_dict, msg):
    mistakes = dict()
    classifications = dict()
    classifications_2_sided = dict()
    for key, ToR_dict in given_IRR.items():
        for arc, ToR in ToR_dict.items():
            key_2_sided, key_2_sided_match = key_analysis((given_IRR[key], I_E_dict), arc)
            add_key_to_set(mistakes, key, arc, key_2_sided and not key_2_sided_match)
            add_key_to_set(classifications_2_sided, key, arc, key_2_sided)
            add_key_to_set(classifications, key, arc)
    with open(f'../Pickles/Mistakes/{msg} Mistakes.pickle', 'wb') as p:
        pickle.dump(mistakes, p)
    with open(f'../Pickles/Classifications/{msg} Classifications 2-Sided.pickle', 'wb') as p:
        pickle.dump(classifications_2_sided, p)
    with open(f'../Pickles/Classifications/{msg} Classifications.pickle', 'wb') as p:
        pickle.dump(classifications, p)


if __name__ == '__main__':
    # p1 = mp.Process(target=secondary_heuristic_analysis, args=(relevant_sets, I_E_dict, 'Sets Dictionary'))
    # p2 = mp.Process(target=secondary_heuristic_analysis, args=(relevant_remarks, I_E_dict, 'Remarks Dictionary'))
    # p1.start()
    # p2.start()
    # p1.join()
    # p2.join()
    secondary_heuristic_analysis(relevant_remarks, I_E_dict, 'Remarks Dictionary')
    secondary_heuristic_analysis(relevant_sets, I_E_dict, 'Sets Dictionary')