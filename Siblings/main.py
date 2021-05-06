import pickle
import codecs
import re
import time
import csv
import matplotlib.pyplot as plt


MailDict = dict()
OrgDict = dict()
MNTDict = dict()
AdminDict = dict()
techDict = dict()
notifyDict = dict()
siblingDict = dict()
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:"
st = time.time()
forbidden_list = list()
sets_siblings = dict()

with open("./../../Pickles/DateDict.pickle", "rb") as p:
    dateDict = pickle.load(p)
with open("./../../Pickles/Sets DateDict.pickle", "rb") as p:
    sets_dateDict = pickle.load(p)
with open("./../../Pickles/Mem.pickle", "rb") as p:
    memDict = pickle.load(p)


def extract_key(AS):
    key = "AS" + (AS.lower().split("as")[1]).split("\n")[0]
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
                MailDict[domain] = list()
            MailDict[domain] = list(set(MailDict[domain] + [key]))


def org_analysis(block, key):
    global OrgDict, dateDict
    delim_remove = 'org:'
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for org in (rem.split(delim_remove))[1:]:
            if 'org-' not in org.lower():
                return
            organization = org.lower().split('org-')[1].split('-')[0]
            if organization not in OrgDict.keys():
                OrgDict[organization] = []
            OrgDict[organization] = list(set(OrgDict[organization] + [key]))


def field_analysis(block, field_dict, field_delim, key, is_sets = False):
    delim_remove = field_delim
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for field in (rem.split(delim_remove))[1:]:
            field_value = field.strip(" \n\t")
            if field_value not in field_dict.keys():
                field_dict[field_value] = []
            if not is_sets:
                field_dict[field_value] = list(set(field_dict[field_value] + [key]))
            else:
                field_dict[field_value] = list(set(field_dict[field_value] + key))



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


def plot_dict_hist(dic, graphtitle, xlabel='len of list', ylabel='# of list with len x'):
    y = [len(val) for val in dic.values()]
    x = [i for i in range(min(y), max(y) + 1)]
    y = [y.count(i) for i in x]
    plt.plot(x, y)
    plt.grid()
    plt.yticks([int(max(y) / 50) * i for i in range(50)] + [int(2 * max(y)/250) * i for i in range(int(2 * max(y)/50))])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.suptitle(graphtitle)
    plt.show()


f = [codecs.open(f"./../../Sources/{i+1}.db", encoding='ISO-8859-1') for i in range(61)]
for file in f:
    print(time.time() - st)
    if file is None: continue
    block_list = file.read().split("\n\n")
    block_list_analysis(block_list)
    for block in block_list:
        if not block.startswith("as-set:"): continue
        set_name = extract_setname(block)
        date = dateDict.get(set_name, 0)
        if date != 0 and str(date) not in block and\
            str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:] not in block: continue
        field_analysis(block, sets_siblings, 'mnt-by:', memDict.get(set_name, []), is_sets=True)


sibling_insertion(MailDict, 'domain')
sibling_insertion(OrgDict, 'org')
sibling_insertion(MNTDict, 'mnt-by', max_len=100)
sibling_insertion(AdminDict, 'admin')
sibling_insertion(techDict, 'tech')
sibling_insertion(notifyDict, 'notify')

plot_dict_hist(MailDict, 'MailDict')
plot_dict_hist(OrgDict, 'OrgDict')
plot_dict_hist(MNTDict, 'MNTDict')
plot_dict_hist(AdminDict, 'AdminDict')
plot_dict_hist(techDict, 'techDict')
plot_dict_hist(notifyDict, 'notifyDict')


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


with open("./../../Pickles/SiblingsDict.pickle", "wb") as p:
    pickle.dump(siblingDict, p)


with open("./../../Example Files/Siblings.csv", mode='w', newline='') as f:
    fwrite = csv.writer(f, delimiter=' ', dialect='excel')
    fwrite.writerow(['AS1', 'AS2', 'ToR', 'Heuristic'])
    for k in siblingDict.keys():
        w = [k[0][2:], k[1][2:], siblingDict[k][0], siblingDict[k][1]]
        fwrite.writerow(w)

