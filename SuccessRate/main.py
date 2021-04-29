import pickle
import re
import time
import csv
from os import path
from datetime import datetime


path = path.abspath(path.dirname(__file__))
with open(path + "\..\Pickles\IRR_Confidence.pickle", "rb") as p:
    conf_dict = pickle.load(p)
    IRR = {}
    for k, v in conf_dict.items():
        IRR[k] = v[0]
with open(path + "\..\Pickles\IRR.pickle", "rb") as p:
    IRR1 = pickle.load(p)
with open(path + "\..\Pickles\IRRv2.pickle", "rb") as p:
    IRR2 = pickle.load(p)
with open(path + "\..\Pickles\IRRv3.pickle", "rb") as p:
    IRR3 = pickle.load(p)
with open(path + "\..\Pickles\Ref.pickle", "rb") as p:
    Ref = pickle.load(p)
log = open(path + '/../Example Files/Logs/%s.txt' % datetime.now().strftime('%d.%m.%y %H;%M;%S'), 'w')


def LOG(str):
    global log
    log.write(str)


def phase_comparison():
    correct = 0
    not_correct = 0
    global IRR, IRR1
    for key in IRR.keys():
        if key in IRR1.keys() and key in Ref.keys():
            if IRR1[key] == Ref[key] and IRR[key] == IRR[key]:
                correct += 1
            if IRR1[key] == Ref[key] and IRR[key] != IRR1[key] and IRR[key] != "P2P":
                not_correct += 1
    return correct, not_correct


def coverage(given_IRR, key, All_coverage_AS):
    if IRR[key] != 'Unknown':
        All_coverage_AS.append(key[0])
        All_coverage_AS.append(key[1])


def is_match(class1, class2):
    return 1 if class1 == class2 else 0


def key_analysis(given_dicts, key1, reverse=False):
    dict1, dict2 = given_dicts
    key2 = reversed(key1) if reverse else key1
    if key1 not in dict1.keys() or key2 not in dict2.keys():
        return 0, 0
    if dict1[key1] == 'Unknown' or dict2[key2] == 'Unknown':
        return 0, 0
    match = (not reverse) * is_match(dict1[key1], dict2[key2])\
        + reverse * is_match(dict1[key1], reversed(dict2[key2]))
    return 1, match


def IRR_analysis(given_IRR):
    global Ref
    matching_classifications = 0
    two_sided_classifications = 0
    two_sided_agreements = 0
    unknown = list(given_IRR.values()).count('Unknown')
    number_of_ToRs_in_our_IRR = len(list(given_IRR.keys())) - unknown
    number_of_ToRs_in_ref_IRR = len(list(Ref.keys()))
    known_keys_in_both = 0
    #correct, not_correct = phase_comparison()
    confusion_matrix = {
        'P2P': {
            'P2P': 0,
            'P2C': 0,
            'C2P': 0
        },
        'P2C': {
            'P2P': 0,
            'P2C': 0,
            'C2P': 0
        },
        'C2P': {
            'P2P': 0,
            'P2C': 0,
            'C2P': 0
        }
    }
    # for key in given_IRR.keys():
    #     if key[::-1] in given_IRR:
    #         if given_IRR[key] == 'Unknown' or given_IRR[reversed(key)] == 'Unknown':
    #             continue
    #         if given_IRR[key] == reversed(given_IRR[reversed(key)]):
    #             agreements += 1
    #         else:
    #             conflicts += 1
    for key in given_IRR.keys():
        key_in_both_dicts, key_match = key_analysis((given_IRR, Ref), (key, key))
        known_keys_in_both += key_in_both_dicts
        matching_classifications += key_match
        key_2_sided, key_2_sided_match = key_analysis((given_IRR, given_IRR), (key, reversed(key)), True)
        two_sided_classifications += key_2_sided
        two_sided_agreements += key_2_sided_match
        if not key_in_both_dicts: continue
        confusion_matrix[Ref[key]][given_IRR[key]] += 1
        coverage(given_IRR, key)
    All_coverage_AS = list(set(All_coverage_AS))
    P2P = [confusion_matrix['P2P']['P2P'], confusion_matrix['P2P']['P2C'], confusion_matrix['P2P']['C2P']]
    P2C = [confusion_matrix['P2C']['P2P'], confusion_matrix['P2C']['P2C'], confusion_matrix['P2C']['C2P']]
    C2P = [confusion_matrix['C2P']['P2P'], confusion_matrix['C2P']['P2C'], confusion_matrix['C2P']['C2P']]

    # print(str(round(float(P2P[0])/(P2P[0] + P2P[1] + P2P[2]) * 100, 2)) + "%")
    padding = 12
    LOG('\tP2C matching rate (relative to CAIDA) is %s\n' % (str(round(float(P2C[1]) / (P2C[1] + P2C[2]) * 100, 2)) + "%"))
    LOG('\tC2P matching rate (relative to CAIDA) is %s\n' % (str(round(float(C2P[2]) / (C2P[1] + C2P[2]) * 100, 2)) + "%"))
    LOG('\tConfusion matrix is:               %s, %s, %s\n'
        % ('IRR P2P'.ljust(padding), 'IRR P2C'.ljust(12), 'IRR C2P'.ljust(padding)))
    LOG('\t' + ' ' * len('Confusion matrix is:\t') + '%s, %s, %s, %s\n' % ('CAIDA P2P'.rjust(padding),
        str(P2P[0]).rjust(padding), str(P2P[1]).rjust(padding), str(P2P[2]).rjust(padding)))
    LOG('\t' + ' ' * len('Confusion matrix is:\t') + '%s, %s, %s, %s\n' % ('CAIDA P2C'.rjust(padding),
        str(P2C[0]).rjust(padding), str(P2C[1]).rjust(padding), str(P2C[2]).rjust(padding)))
    LOG('\t' + ' ' * len('Confusion matrix is:\t') + '%s, %s, %s, %s\n' % ('CAIDA C2P'.rjust(padding),
        str(C2P[0]).rjust(padding), str(C2P[1]).rjust(padding), str(C2P[2]).rjust(padding)))

    LOG('\tWe can classify %s ToRs\n' % number_of_ToRs_in_our_IRR)
    LOG('\toverall matching rate is: %s\n' % (str(round(float(matching_classifications) / known_keys_in_both * 100, 2)) + "%"))
    LOG("\tNumber of Matching Classifications: %s\n" % matching_classifications)
    LOG("\tNumber of Known ToRs in this and CAIDA's IRR: %s\n" % known_keys_in_both)
    LOG("\tNumber of ToRs in Ref IRR: %s\n" % number_of_ToRs_in_ref_IRR)
    LOG('\tratio of 2 - sided agreements is %s%%\n' % round(two_sided_agreements/two_sided_classifications, 2))
    LOG('\tnumber of conflicts is %s%%\n' % round(1 - two_sided_agreements/two_sided_classifications, 2))


def log_IRR(IRR, msg):
    LOG(msg + '\n')
    IRR_analysis(IRR)
    LOG('\n')


log_IRR(IRR1, 'I/E Dictionary:')
log_IRR(IRR2, 'Remarks Dictionary:')
log_IRR(IRR3, 'Sets Dictionary:')
log_IRR(IRR, 'Overall Dictionary:')
log.close()
# with open(path + '/../Example Files/RefCompare.csv', mode='w', newline='') as f:
#     fwrite = csv.writer(f, delimiter=',')
#     fwrite.writerow(['AS1', 'AS2', 'IRR Prediction', 'Caida Prediction'])
#     for k in Ref.keys():
#         if k in IRR.keys():
#             w = [k[0][2:], k[1][2:], IRR[k], Ref[k], ' ']
#         else:
#             w = [k[0][2:], k[1][2:], "Doesn't Exist", Ref[k], ' ']
#         fwrite.writerow(w)
#     for k in (list(set(list(Ref.keys()) + list(IRR.keys())) - set(Ref.keys()))):
#         w = [k[0][2:], k[1][2:], IRR[k], "Doesn't Exist", ' ']
#         fwrite.writerow(w)


