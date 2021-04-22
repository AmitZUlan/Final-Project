import pickle
import codecs
import re
import time
from os import path

path = path.abspath(path.dirname(__file__))
ASDict = {}
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:"

st = time.time()


def extract_key(AS):
    key = "AS" + (AS.lower().split("as")[1]).split("\n")[0]
    if '#' in key:
        key = key.split('#')[0]
    return key


def policy_analysis(policy):
    i = 0
    policylist = []
    while policy[i] != "accept" and policy[i] != "announce" and policy[i] != "import": i += 1
    if i + 1 == len(policy):
        policy = 'Error'
    if policy[i + 1] == "any":
        policy = 'A'
    else:
        i += 1
        while i < len(policy):
            if policy[i].isnumeric():
                policylist.append("AS" + policy[i].upper())
            if policy[i].lower().startswith("as") and policy[i][2:].isnumeric():
                policylist.append(policy[i].upper())
            if '#' in policy[i]:
                policy = policy[:i]
                continue
            if policy[i].lower().startswith("as"):
                policylist.append(policy[i].upper())
            i += 1
        policy = 'O'
    return policy, policylist


def import_analysis(imp, delim):
    policylist = None
    if "ipv6" in imp.lower():
        return None, None, None
    if delim in imp.lower():
        imp = imp.lower().split(delim)[1]
    source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", imp.lower())
    while "" in source: source.remove("")
    if not source:
        return None, None, None
    policy = source
    source = source[0]
    if source.isnumeric():
        source = "AS" + source
    if source == "as":
        if policy[1].isnumeric():
            source = source + policy[1]
        else:
            source = source + '-' + policy[1]
    if '#' in source:
        source = source.split('#')[0]
    source = source.upper()
    while "" in policy: policy.remove("")
    if "accept" not in policy and "announce" not in policy and "import" not in policy:
        policy = "Error"
    else:
        policy, policylist = policy_analysis(policy)
    return source, policy, policylist


def add_source(key, source, policy, policylist, imporexp):
    global ASDict
    if policy is None:
        return
    if source not in ASDict[key][imporexp].keys():
        ASDict[key][imporexp][source] = []
    if policy == 'A':
        ASDict[key][imporexp][source] = policy
    if policy == 'Error' and ASDict[key][imporexp][source] == []:
        ASDict[key][imporexp][source] = policy
    if policy == 'O':
        if ASDict[key][imporexp][source] != 'A' and policylist:
            if ASDict[key][imporexp][source] == "Error":
                ASDict[key][imporexp][source] = []
            ASDict[key][imporexp][source] = list(set(ASDict[key][imporexp][source] + policylist))


def AS_analysis(block, delim_remove):
    global ASDict
    if not block.startswith("aut-num:"):
        return
    key = extract_key(block)
    if key not in ASDict.keys():
        ASDict[key] = ({}, {})
    for exp in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for imp in (exp.split(delim_remove))[1:]:
            if delim_remove == "import:":
                source, policy, policylist = import_analysis(imp, "from ")
                add_source(key, source, policy, policylist, 0)
            if delim_remove == "export:":
                source, policy, policylist = import_analysis(imp, "to ")
                add_source(key, source, policy, policylist, 1)


def block_list_analysis(block_list, delim_remove):
    for block in block_list:
        block = block + "\n"
        AS_analysis(block, delim_remove)


f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../Sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
for file in f:
    print(time.time() - st)
    if file is not None:
        block_list = file.read().split("\n\n")
        block_list_analysis(block_list.copy(), "import:")
        block_list_analysis(block_list.copy(), "export:")

count = 0
for AS in ASDict.keys():
    if len(ASDict[AS][0].keys()) == 0:
        count += 1
print(count)
print(len(list(ASDict.keys())))
with open(path + "/../Pickles/ASDict.pickle", "wb") as p:
    pickle.dump(ASDict, p)
print(ASDict)

