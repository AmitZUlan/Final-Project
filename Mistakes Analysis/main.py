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


def coverage(given_IRR, key, AS_coverage_set1, AS_coverage_set2):
    if given_IRR[key] == 'Unknown': return
    AS_coverage_set1.add(key[0])
    for AS in key:
        AS_coverage_set2.add(AS)


def reverse_match(dict, key, keys):
    if dict.get(key, 'Unknown') == 'Unknown' or dict.get(key[::-1], 'Unknown') == 'Unknown':
        return 0, 0
    return 1, dict[key] == dict[key[::-1]][::-1]


def check_mistakes(given_IRR, msg, mistakes, classifications_2_sided, classifications, mistake_threshold):
    assert 0 <= mistake_threshold <= 100, f"{mistake_threshold}"
    print(f'%s: Starting Process: {msg[:-1]}, Mistake Threshold is {mistake_threshold}%%.' % datetime.now().strftime('%H:%M:%S'))
    results = list()
    for i in range(2):
        forbidden_list = set()
        two_sided_classifications = 0
        two_sided_agreements = 0
        AS_coverage_set_1_side = set()
        AS_coverage_set_2_side = set()
        for AS, count in mistakes.items():
            mistake_ratio = len(count) / len(classifications[AS]) if i else len(count) / len(classifications_2_sided[AS])
            assert 0 <= mistake_ratio <= 1
            if mistake_ratio > mistake_threshold/100:
                forbidden_list.add(AS)
        keys = given_IRR.keys()
        for key in keys:
            if key[0] in forbidden_list: continue
            key_2_sided, key_2_sided_match = reverse_match(given_IRR, key, keys)
            two_sided_classifications += key_2_sided
            two_sided_agreements += key_2_sided_match
            coverage(given_IRR, key, AS_coverage_set_1_side, AS_coverage_set_2_side)
        results += [(mistake_threshold, two_sided_classifications, two_sided_agreements,
                    AS_coverage_set_1_side, AS_coverage_set_2_side, forbidden_list)]
    with open(f'./../../Pickles/Mistakes/{msg[:-1]}/Mistake Threshold is {mistake_threshold}%.pickle', 'wb') as p:
        pickle.dump(results, p)
    print(f'%s: {msg[:-1]}, Mistake Threshold is {mistake_threshold}%%, Process Finished.' % datetime.now().strftime('%H:%M:%S'))


def check_date(given_IRR, msg, dateDict, date_threshold):
    print(f'%s: Starting Process: {msg[:-1]}, Earliest Date is {date_threshold}.' % datetime.now().strftime('%H:%M:%S'))
    forbidden_list = set(AS for AS, date in dateDict.items() if date_threshold > date)
    results = results_extraction(given_IRR, forbidden_list, date_threshold)
    with open(f'./../../Pickles/Dates/{msg[:-1]}/Oldest Date={date_threshold}.pickle', 'wb') as p:
        pickle.dump(results, p)
    print(f'%s: {msg[:-1]}, Earliest Date is {date_threshold}, Process Finished.' % datetime.now().strftime('%H:%M:%S'))


def results_extraction(given_IRR, forbidden_list, date_threshold):
    results = list()
    two_sided_classifications = 0
    two_sided_agreements = 0
    AS_coverage_set_1_side = set()
    AS_coverage_set_2_side = set()
    keys = given_IRR.keys()
    for key in keys:
        if key[0] in forbidden_list: continue
        key_2_sided, key_2_sided_match = reverse_match(given_IRR, key, keys)
        two_sided_classifications += key_2_sided
        two_sided_agreements += key_2_sided_match
        coverage(given_IRR, key, AS_coverage_set_1_side, AS_coverage_set_2_side)
    results += [(date_threshold, two_sided_classifications, two_sided_agreements,
                 AS_coverage_set_1_side, AS_coverage_set_2_side, forbidden_list)]
    return results


if __name__ == '__main__':
    args_list = [
        (IRR3, 'Sets Dictionary:'),
        (IRR2, 'Remarks Dictionary:'),
        (IRR1, 'I_E Dictionary:'),
    ]

    processes = list()

    # for arg in args_list:
    #     with open(f'./../../Pickles/Mistakes/{arg[1][:-1]} Mistakes.pickle', 'rb') as p:
    #         mistakes = pickle.load(p)
    #     with open(f'./../../Pickles/Classifications/{arg[1][:-1]} Classifications 2-Sided.pickle', 'rb') as p:
    #         classifications_2_sided = pickle.load(p)
    #     with open(f'./../../Pickles/Classifications/{arg[1][:-1]} Classifications.pickle', 'rb') as p:
    #         classifications = pickle.load(p)
    #
    #     count = 0
    #     for threshold in range(101):
    #         args = (arg[0], arg[1], mistakes, classifications_2_sided, classifications, threshold)
    #         p = mp.Process(target=check_mistakes, args=args)
    #         processes.append(p)
    #         p.start()
    #         count += 1
    #
    #         if count > 14:
    #             processes[0].join()
    #             count -= 1
    #             processes.remove(processes[0])
    #     if count != 0:
    #         for process in processes:
    #             process.join()

    for arg in args_list[1:]:
        with open("./../../Pickles/DateDict.pickle", "rb") as p:
            DateDict = pickle.load(p)

        count = 0
        for date_threshold in range(2020 * 10 ** 4, 1950 * 10 ** 4, -10 ** 4):
            args = (arg[0], arg[1], DateDict, date_threshold)
            p = mp.Process(target=check_date, args=args)
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

