import pickle
import multiprocessing as mp
from datetime import datetime

if __name__ == '__main__':
    with open("../Pickles/IRR.pickle", "rb") as p:
        IRR1 = pickle.load(p)
    with open("../Pickles/IRRv2.pickle", "rb") as p:
        IRR2 = pickle.load(p)
    with open("../Pickles/IRRv3.pickle", "rb") as p:
        IRR3 = pickle.load(p)


def coverage(given_IRR, key, AS_coverage_set1, AS_coverage_set2):
    if given_IRR[key] == 'Unknown': return
    AS_coverage_set1.add(key[0])
    for AS in key:
        AS_coverage_set2.add(AS)


def reverse_match(_dict, rev_dict, key, forbidden_list):
    if _dict.get(key, 'Unknown') == 'Unknown' or rev_dict.get(key[::-1], 'Unknown') == 'Unknown' or\
            key[0] in forbidden_list or key[1] in forbidden_list:
        return 0, 0
    return 1, _dict[key] == rev_dict[key[::-1]][::-1]


def check_mistakes(given_IRR, rev_IRR, msg, mistakes, classifications_2_sided, classifications, mistake_threshold):
    assert 0 <= mistake_threshold <= 100, f"{mistake_threshold}"
    print(f'%s: Starting Process: {msg[:-1]}, Mistake Threshold is '
          f'{mistake_threshold}%%.' % datetime.now().strftime('%H:%M:%S'))
    forbidden_list = create_forbidden_list(mistakes, classifications_2_sided, classifications, mistake_threshold, 0)
    results = results_calculation(given_IRR, rev_IRR, forbidden_list)
    forbidden_list = create_forbidden_list(mistakes, classifications_2_sided, classifications, mistake_threshold, 3)
    results += results_calculation(given_IRR, rev_IRR, forbidden_list)
    forbidden_list = create_forbidden_list(mistakes, classifications_2_sided, classifications, mistake_threshold, 5)
    results += results_calculation(given_IRR, rev_IRR, forbidden_list)
    with open(f'../Pickles/Mistakes/{msg[:-1]}/Mistake Threshold is {mistake_threshold}%.pickle', 'wb') as p:
        pickle.dump(results, p)
    print(f'%s: {msg[:-1]}, Mistake Threshold is {mistake_threshold}%%, Process Finished.' % datetime.now().strftime('%H:%M:%S'))


def results_calculation(given_IRR, rev_IRR, forbidden_list):
    keys = given_IRR.keys()
    IRR_dup = dict()
    for key in keys:
        if given_IRR[key] == 'Unknown': continue
        if key[0] in forbidden_list or key in forbidden_list: continue
        IRR_dup[key] = given_IRR[key]
    two_sided_classifications = 0
    two_sided_agreements = 0
    ToR_Count = 0
    AS_coverage_set_1_side = set()
    AS_coverage_set_2_side = set()
    keys = IRR_dup.keys()
    for key in keys:
        ToR_Count += IRR_dup[key] != 'Unknown'
        key_2_sided, key_2_sided_match = reverse_match(IRR_dup, rev_IRR, key, forbidden_list)
        two_sided_classifications += key_2_sided
        two_sided_agreements += key_2_sided_match
        coverage(IRR_dup, key, AS_coverage_set_1_side, AS_coverage_set_2_side)
    ToRs = set.union(
        {k for k in IRR_dup.keys() if k not in forbidden_list and IRR_dup[k] != 'Unknown'},
        {k[::-1] for k in IRR_dup.keys() if k not in forbidden_list and IRR_dup[k] != 'Unknown'},
    )
    results = [(ToR_Count, two_sided_classifications, two_sided_agreements,
                AS_coverage_set_1_side, AS_coverage_set_2_side, forbidden_list, len(ToRs))]
    return results


def min_2_sided_requirement(given_IRR, rev_IRR, msg, mistakes, classifications_2_sided, classifications, min_2_sided):
    print(f'%s: Starting Process: {msg[:-1]}, The Requirement of at least '
          f'{min_2_sided} 2-Sided ToRs.' % datetime.now().strftime('%H:%M:%S'))
    forbidden_list = create_forbidden_list(mistakes, classifications_2_sided, classifications, 100, min_2_sided)
    results = results_calculation(given_IRR, rev_IRR, forbidden_list)
    forbidden_list = create_forbidden_list(mistakes, classifications_2_sided, classifications, 20, min_2_sided)
    results += results_calculation(given_IRR, rev_IRR, forbidden_list)
    forbidden_list = create_forbidden_list(mistakes, classifications_2_sided, classifications, 10, min_2_sided)
    results += results_calculation(given_IRR, rev_IRR, forbidden_list)
    with open(f'../Pickles/2-Sides Requirement/{msg[:-1]}/Requirement of at least '
              f'{min_2_sided} 2-Sided ToRs.pickle', 'wb') as p:
        pickle.dump(results, p)
    print(f'%s: {msg[:-1]}, Requirement of at least '
          f'{min_2_sided} 2-Sided ToRs, Process Finished.' % datetime.now().strftime('%H:%M:%S'))


def create_forbidden_list(mistakes, classifications_2_sided, classifications, mistake_threshold, min_2_sided):
    forbidden_list = set()
    for AS, classification_arcs in classifications.items():
        if len(classifications_2_sided.get(AS, set())) < min_2_sided and\
                len(classifications_2_sided.get(AS, set())) != len(classification_arcs):
            forbidden_list.add(AS)
            forbidden_list.update(classification_arcs)
            continue
        mistake_ratio = len(mistakes.get(AS, set())) / len(classifications_2_sided.get(AS, {1}))
        assert 0 <= mistake_ratio <= 1
        if mistake_ratio <= mistake_threshold/100: continue
        forbidden_list.add(AS)
        forbidden_list.update(classification_arcs)
    return forbidden_list


if __name__ == '__main__':
    args_list = [
        (IRR3, IRR1, 'Sets Dictionary:'),
        (IRR2, IRR1, 'Remarks Dictionary:'),
        (IRR1, IRR1, 'I_E Dictionary:'),
    ]

    processes = list()

    for arg in args_list:
        with open(f'../Pickles/Mistakes/{arg[2][:-1]} Mistakes.pickle', 'rb') as p:
            mistakes = pickle.load(p)
        with open(f'../Pickles/Classifications/{arg[2][:-1]} Classifications 2-Sided.pickle', 'rb') as p:
            classifications_2_sided = pickle.load(p)
        with open(f'../Pickles/Classifications/{arg[2][:-1]} Classifications.pickle', 'rb') as p:
            classifications = pickle.load(p)

        count = 0
        for threshold in range(101):
            args = (*arg, mistakes, classifications_2_sided, classifications, threshold)
            p = mp.Process(target=check_mistakes, args=args)
            processes.append(p)
            p.start()
            count += 1

            if count > 14:
                processes[0].join()
                count -= 1
                processes.remove(processes[0])

        for threshold in range(11):
            args = (*arg, mistakes, classifications_2_sided, classifications, threshold)
            p = mp.Process(target=min_2_sided_requirement, args=args)
            processes.append(p)
            p.start()
            count += 1

            if count > 14:
                processes[0].join()
                count -= 1
                processes.remove(processes[0])

        if count != 0:
            for process in processes:
                process.join()


