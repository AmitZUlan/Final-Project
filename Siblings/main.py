import pickle
import codecs
import re
import time
from os import path
import csv
import matplotlib.pyplot as plt


path = path.abspath(path.dirname(__file__))
MailDict = dict()
OrgDict = dict()
MNTDict = dict()
AdminDict = dict()
techDict = dict()
notifyDict = dict()
ASDict = dict()
siblingDict = dict()
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:"
st = time.time()
forbidden_list = list()


def extract_key(AS):
    key = "AS" + (AS.lower().split("as")[1]).split("\n")[0]
    if '#' in key:
        key = key.split('#')[0]
    return key


def date_init(block):
    global ASDict
    delim_remove = 'changed:'
    if not block.startswith("aut-num:"):
        return
    key = extract_key(block)
    if key == 'AS40630':
        a = 3
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for sib in (rem.split(delim_remove))[1:]:
            date = re.split(' |\n', sib)
            i = 0
            while i < len(date) - 1 and not date[i].isnumeric():
                i += 1
            date = (int(date[i]) if date[i].isnumeric() else 0)
            if key in ASDict.keys():
                if ASDict[key] > date:
                    return
            ASDict[key] = date


def changed_analysis(block):
    global MailDict, ASDict
    delim_remove = 'changed:'
    if not block.startswith("aut-num:"):
        return
    key = extract_key(block)
    if key in ASDict.keys() and ASDict[key] != 0 and str(ASDict[key]) not in block:
        return
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for sib in (rem.split(delim_remove))[1:]:
            if '@' not in sib:
                return
            domain = (sib.split('@')[1]).split(' ')[0]
            if domain not in MailDict.keys():
                MailDict[domain] = list()
            MailDict[domain] = list(set(MailDict[domain] + [key]))


def org_analysis(block):
    global OrgDict, ASDict
    delim_remove = 'org:'
    if not block.startswith("aut-num:"):
        return
    key = extract_key(block)
    if key in ASDict.keys() and ASDict[key] != 0 and str(ASDict[key]) not in block:
        return
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for org in (rem.split(delim_remove))[1:]:
            if 'org-' not in org.lower():
                return
            organization = org.lower().split('org-')[1].split('-')[0]
            if organization not in OrgDict.keys():
                OrgDict[organization] = []
            OrgDict[organization] = list(set(OrgDict[organization] + [key]))


def field_analysis(block, field_dict, field_delim):
    global ASDict
    delim_remove = field_delim
    if not block.startswith("aut-num:"):
        return
    key = extract_key(block)
    if key in ASDict.keys() and ASDict[key] != 0 and str(ASDict[key]) not in block:
        return
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for field in (rem.split(delim_remove))[1:]:
            field_value = field.strip(" \n\t")
            if field_value not in field_dict.keys():
                field_dict[field_value] = []
            field_dict[field_value] = list(set(field_dict[field_value] + [key]))


def block_list_analysis(block_list):
    for block in block_list:
        block = block + "\n"
        date_init(block)
    for block in block_list:
        block = block + "\n"
        changed_analysis(block)
        org_analysis(block)
        field_analysis(block, MNTDict, 'mnt-by:')
        field_analysis(block, AdminDict, 'admin-c:')
        field_analysis(block, techDict, 'tech-c:')
        field_analysis(block, notifyDict, 'notify:')


def sibling_insertion(source_dict, field, forbidden_list=list(), max_len=None):
    global siblingDict
    for key in source_dict.keys():
        if len(source_dict[key]) < 2 or 'dum' in key.lower() or key.lower() in forbidden_list\
                or (max_len is not None and max_len < len(source_dict[key])):
            continue
        for value in source_dict[key]:
            HisSiblings = source_dict[key].copy()
            HisSiblings.remove(value)
            for sibling in HisSiblings:
                if value != sibling:
                    if (value, sibling) not in siblingDict.keys():
                        siblingDict[(value, sibling)] = ["S2S", '%s=%s' % (field, key)]
                    else:
                        siblingDict[(value, sibling)][1] += ', %s=%s' % (field, key)


f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
for file in f:
    print(time.time() - st)
    if file is not None:
        block_list = file.read().split("\n\n")
        block_list_analysis(block_list)


sibling_insertion(MailDict, 'domain')
sibling_insertion(OrgDict, 'org')
sibling_insertion(MNTDict, 'mnt-by', max_len=30)
sibling_insertion(AdminDict, 'admin')
sibling_insertion(techDict, 'tech')
sibling_insertion(notifyDict, 'notify')


print(siblingDict)
print(OrgDict)
#for lis in OrgDict.values():
    #if len(lis) > 1:
        #print(len(lis))
print(MNTDict)
a = list()
for lis in MNTDict.values():
    if len(lis) > 1:
        #print(len(lis))
        a.append((len(lis)))
b = [i for i in range(25)]
plt.hist(a, bins=b)
plt.show()

with open(path + "/../Pickles/SiblingsDict.pickle", "wb") as p:
    pickle.dump(siblingDict, p)


with open(path + '/../Example Files/Siblings.csv', mode='w', newline='') as f:
    fwrite = csv.writer(f, delimiter=' ', dialect='excel')
    fwrite.writerow(['AS1', 'AS2', 'ToR', 'Heuristic'])
    for k in siblingDict.keys():
        w = [k[0][2:], k[1][2:], siblingDict[k][0], siblingDict[k][1]]
        fwrite.writerow(w)

