import os
import pickle
import codecs
import re
import time
import csv
import matplotlib.pyplot as plt
from collections import Counter

MailDict = dict()
OrgDict = dict()
MNTDict = dict()
AdminDict = dict()
techDict = dict()
notifyDict = dict()
AS_Siblings = dict()
siblingDict = dict()
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address" \
        ":|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local" \
        "-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref" \
        ":|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified" \
        ":|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block" \
        ":|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type" \
        ":|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:|mnt-irt: "
st = time.time()
forbidden_list = list()
sets_siblings = dict()

with open("../Pickles/DateDict.pickle", "rb") as p:
    dateDict = pickle.load(p)
with open("../Pickles/Sets DateDict.pickle", "rb") as p:
    sets_dateDict = pickle.load(p)
with open("../Pickles/Mem.pickle", "rb") as p:
    memDict = pickle.load(p)
with open("../Pickles/Names.pickle", "rb") as p:
    NamesDict = pickle.load(p)


def extract_key(AS):
    key = "AS" + (AS.lower().split("as")[1]).split("\n")[0].strip()
    if '#' in key:
        key = key.split('#')[0]
    return key


def extract_setname(block):
    global ASSets
    set_name = ((block.split("as-set:")[1]).split("\n")[0]).strip()
    if '#' in set_name:
        set_name = set_name.split("#")[0]
    return set_name


def changed_analysis(block, key):
    global MailDict, dateDict
    delim_remove = 'changed:'
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for sib in (rem.split(delim_remove))[1:]:
            if '@' not in sib:
                return
            domain = (sib.split('@')[1]).split(' ')[0]
            if domain not in MailDict.keys():
                MailDict[domain] = set()
            MailDict[domain].add(key)


def org_analysis(block, key):
    global OrgDict, dateDict
    delim_remove = 'org:'
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for org in (rem.split(delim_remove))[1:]:
            if 'org-' not in org.lower():
                return
            organization = org.lower().split('org-')[1].split('-')[0]
            if organization not in OrgDict.keys():
                OrgDict[organization] = set()
            OrgDict[organization].add(key)


def field_analysis(block, field_dict, field_delim, key, is_sets=False):
    delim_remove = field_delim
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for field in (rem.split(delim_remove))[1:]:
            field_value = field.split('\n')[0].strip(" \t")
            if field_value not in field_dict.keys():
                field_dict[field_value] = set()
            if not is_sets:
                field_dict[field_value].add(key)
            else:
                field_dict[field_value].update(key)


def mnt_sibling_insertion(mnt_dict):
    # global AS_Siblings
    new_mnt_dict = dict()
    for key in mnt_dict.keys():
        if 'as' not in key.lower(): continue
        if len(mnt_dict[key]) < 2: continue
        if 'AS' + key.lower().split('as')[1] not in mnt_dict[key]:
            if not key.lower().split('as')[1].split('-')[0].isnumeric():
                continue
            else:
                new_mnt_dict[key] = new_mnt_dict.get(key, set())
                new_mnt_dict[key].add('AS' + key.lower().split('as')[1].split('-')[0])
            new_mnt_dict[key] = new_mnt_dict.get(key, set())
            new_mnt_dict[key].update(mnt_dict[key])
    return new_mnt_dict
        # for AS in mnt_dict[key]:
        #     AS_Siblings[AS] = AS_Siblings.get(AS, dict())
        #     siblings_list = mnt_dict[key].copy()
        #     siblings_list.remove(AS)
        #     AS_Siblings[AS][f"{field}={key}"] = siblings_list


def block_list_analysis(block_list):
    for block in block_list:
        block = block + "\n"
        if not block.startswith("aut-num:") and not block.startswith("*xx-num:"): continue
        key = extract_key(block)
        date = dateDict.get(key, 0)
        if date != 0 and str(date) not in block and \
            str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:] not in block: continue
        changed_analysis(block, key)
        org_analysis(block, key)
        field_analysis(block, MNTDict, 'mnt-by:', key)
        field_analysis(block, AdminDict, 'admin-c:', key)
        field_analysis(block, techDict, 'tech-c:', key)
        field_analysis(block, notifyDict, 'notify:', key)


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


def plot_dict_hist(dic, graphtitle, xlabel='len of list', ylabel='# of list with len x', max_len=11, CDF=False, norm=False):
    y = [len(val) for val in dic.values() if 1 < len(val) < max_len]
    plt.hist(y, bins=list(range(max_len + 1)), cumulative=CDF, range=(1, max_len), align='left', density=norm)
    Count_y = Counter(y)
    keys = list(Count_y.keys())
    keys.sort()
    # summary = len([len(val) for val in dic.values()])
    summary = sum([y.count(xj) for xj in keys])
    if norm:
        for xi in keys:
            Count_y[xi] /= summary
    if CDF:
        for xi in keys:
            Count_y[xi] += Count_y.get(xi - 1, 0)
    x, y = zip(*Count_y.items())
    plt.scatter(x, y)
    for xi, yi in zip(x, y):
        label = f"({xi}, {round(yi, 2)})"
        plt.annotate(label,
                     (xi, yi),
                     textcoords="offset points",
                     xytext=(20, 3),
                     ha='right',
                     )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    title = graphtitle
    title += ' Normalized' if norm else ''
    title += ' CDF' if CDF else ''
    plt.suptitle(title)
    if not os.path.exists(f'../Example Files/Plots'):
        os.mkdir(f'../Example Files/Plots')
    if not os.path.exists(f'../Example Files/Plots/Siblings'):
        os.mkdir(f'../Example Files/Plots/Siblings')
    plt.savefig(f"../Example Files/Plots/Siblings/{title}.png", dpi=300)
    plt.close()


def concat_siblings():
    global siblingDict
    for AS, sibling_indicator in AS_Siblings.items():
        sibling_set = set()
        sibling_set.update(*sibling_indicator.values())
        for sibling in sibling_set:
            comment = [indicator for indicator in sibling_indicator.keys() if sibling in sibling_indicator[indicator]]
            comment = ', '.join(comment)
            siblingDict[(AS, sibling)] = ('S2S', comment)


for i in range(61):
    with codecs.open(f"../Sources/{i}.db", encoding='ISO-8859-1') as file:
        print(f'{i}:', time.time() - st)
        if file is None: continue
        block_list = file.read().split("\n\n")
        block_list_analysis(block_list)
        for block in block_list:
            if not block.startswith("as-set:"): continue
            set_name = extract_setname(block)
            date = dateDict.get(set_name, 0)
            if date != 0 and str(date) not in block and\
                str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:] not in block: continue
            if set_name not in memDict: continue
            field_analysis(block, sets_siblings, 'mnt-by:', memDict[set_name], is_sets=True)

MNT_AS_Dict = mnt_sibling_insertion(MNTDict)
sets_AS_Dict = mnt_sibling_insertion(sets_siblings)

dicts = (MailDict, OrgDict, MNTDict, AdminDict, techDict, notifyDict, NamesDict, MNT_AS_Dict, sets_AS_Dict)
fields = ('domain', 'org', 'mnt-by', 'admin', 'tech', 'notify')
titles = ('MailDict', 'OrgDict', 'MNTDict', 'AdminDict', 'techDict', 'notifyDict', 'NamesDict', 'MNTDict by AS', 'Sets Siblings')

for field_dict, title in zip(dicts, titles):
    for i in range(4):
        plot_dict_hist(field_dict, title, CDF=bool(i & 1), norm=bool(i & 2))

for field_dict, title in zip(dicts, titles):
    if not os.path.exists(f'../Pickles/Siblings'):
        os.mkdir(f'../Pickles/Siblings')
    with open(f"../Pickles/Siblings/{title}.pickle", "wb") as p:
        pickle.dump(field_dict, p)


for field_dict, field in zip(dicts, fields):
    sibling_insertion(field_dict, field, max_len=5)

sibling_insertion(NamesDict, 'name', max_len=5)
sibling_insertion(MNT_AS_Dict, 'mnt-by-as', max_len=5)
sibling_insertion(sets_AS_Dict, 'set_mnt-by-as', max_len=5)  # AS1, AS2 S2S  AS2, AS3 S2S


concat_siblings()


with open("../Pickles/SiblingsDict.pickle", "wb") as p:
    pickle.dump(siblingDict, p)


with open("../Example Files/Siblings Threshold=5.csv", mode='w', newline='') as f:
    writer = csv.writer(f, dialect='excel')
    writer.writerow(['AS1', 'AS2', 'ToR', 'Heuristic'])
    for k in siblingDict.keys():
        writer.writerow([k[0][2:], k[1][2:], siblingDict[k][0], siblingDict[k][1]])
