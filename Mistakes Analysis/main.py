import pickle
import multiprocessing as mp
from datetime import datetime

if __name__ == '__main__':
    with open("./../../Pickles/IRR_Confidence_class_only.pickle", "rb") as p:
        IRR = pickle.load(p)
    with open("./../../Pickles/IRR.pickle", "rb") as p:
        IRR1 = pickle.load(p)
    with open("./../../Pickles/IRRv2.pickle", "rb") as p:
        IRR2 = pickle.load(p)
    with open("./../../Pickles/IRRv3.pickle", "rb") as p:
        IRR3 = pickle.load(p)


def coverage(given_IRR, key, AS_coverage_list1, AS_coverage_list2):
    if given_IRR[key] != 'Unknown': return
    if key[0] not in AS_coverage_list1:
        AS_coverage_list1.append(key[0])
    for AS in key:
        if AS not in AS_coverage_list2:
            AS_coverage_list2.append(AS)


def reverse_match(dict, key, keys):
    if key not in keys or key[::-1] not in keys:
        return 0, 0
    if dict[key] == 'Unknown' or dict[key[::-1]] == 'Unknown':
        return 0, 0
    return 1, dict[key] == dict[key[::-1]][::-1]


def check_mistakes(given_IRR, msg, mistakes, mistake_threshold):
    print(f'%s: Starting Process: {msg[:-1]}, Threshold is {mistake_threshold}.' % datetime.now().strftime('%H:%M:%S'))
    forbidden_list = list()
    two_sided_classifications = 0
    two_sided_agreements = 0
    AS_coverage_list_1_side = list()
    AS_coverage_list_2_side = list()
    for AS, count in mistakes.items():
        if count > mistake_threshold:
            forbidden_list.append(AS)
    keys = given_IRR.keys()
    for key in keys:
        if key[0] in forbidden_list: continue
        key_2_sided, key_2_sided_match = reverse_match(given_IRR, key, keys)
        two_sided_classifications += key_2_sided
        two_sided_agreements += key_2_sided_match
        coverage(given_IRR, key, AS_coverage_list_1_side, AS_coverage_list_2_side)
    results = [(mistake_threshold, two_sided_classifications, two_sided_agreements,
                len(AS_coverage_list_1_side), len(AS_coverage_list_2_side))]
    with open(f'./../../Pickles/Mistakes/{msg[:-1]}/Mistake Threshold {mistake_threshold}.pickle', 'wb') as p:
        pickle.dump(results, p)
    print(f'%s: {msg[:-1]}, Mistake Threshold is {mistake_threshold}, Process Finished.' % datetime.now().strftime('%H:%M:%S'))
    return results


if __name__ == '__main__':
    args_list = [
        (IRR2, 'Remarks Dictionary:'),
        (IRR3, 'Sets Dictionary:'),
        (IRR1, 'I_E Dictionary:'),
    ]

    processes = list()
    for arg in args_list:
        with open(f'./../../Pickles/{arg[1][:-1]} Mistakes.pickle', 'rb') as p:
            mistakes = pickle.load(p)

        count = 0
        for threshold in range(1, 25, 1):
            count += 1
            p = mp.Process(target=check_mistakes, args=(arg[0], arg[1], mistakes, threshold))
            processes.append(p)
            p.start()
            if count == 15:
                for process in processes:
                    process.join()
                count = 0
                processes = list()
        if count != 0:
            for process in processes:
                process.join()
