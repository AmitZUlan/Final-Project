import pickle
import codecs
import re
import time
ASDict = dict()
ASNames = dict()
dateDict = dict()
ASNames = dict()
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:"

st = time.time()


def format_date(date_int):
    return


def extract_key(block):
    AS = "AS" + (block.lower().split("as")[1]).split("\n")[0].strip()
    if '#' in AS:
        AS = AS.split('#')[0]
    return AS


def date_init(block, key):
    global dateDict
    delim_remove = 'changed:'
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for field in (rem.split(delim_remove))[1:]:
            date = re.split(' |\n', field.strip())
            i = 0
            while i < len(date) - 1 and not date[i].isnumeric():
                i += 1
            date = (int(date[i]) if date[i].isnumeric() else 0)
            dateDict[key] = max(dateDict.get(key, 0), date)
    delim_remove = 'last-modified:'
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for field in (rem.split(delim_remove))[1:]:
            date = field.split('t')[0].strip()
            date = date.split('-')
            date = ''.join(date)
            date = int(date) if date.isnumeric() else 0
            dateDict[key] = max(dateDict.get(key, 0), date)


def import_analysis(imp, delim):
    policylist = None
    if "ipv6" in imp.lower():
        return None, None, None
    if ' afi ' in imp.lower() and all(word not in imp.lower() for word in ['ipv4', ' any.', 'afi any']):
        return None, None, None
    if delim in imp.lower():
        imp = imp.lower().split(delim)[1]
    source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", imp.lower())
    source = [s for s in source if s != '']
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
        ASDict[key][imporexp][source] = set()
    if policy == 'A':
        ASDict[key][imporexp][source] = policy
    if policy == 'Error' and ASDict[key][imporexp][source] == set():
        ASDict[key][imporexp][source] = policy
    if policy == 'O':
        if ASDict[key][imporexp][source] != 'A' and policylist:
            if ASDict[key][imporexp][source] == "Error":
                ASDict[key][imporexp][source] = set()
            ASDict[key][imporexp][source].update(policylist)


def AS_analysis(block, delim_remove, AS):
    global ASDict, delim
    if AS not in ASDict.keys():
        ASDict[AS] = ({}, {})
    pre_as_word = 'to ' if delim_remove == 'export:' else 'from '
    tuple_index = delim_remove == 'export:'
    if delim_remove != 'import:' and \
            (pre_as_word == 'from ' or not tuple_index): raise ValueError
    for exp in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for imp in (exp.split(delim_remove))[1:]:
            source, policy, policylist = import_analysis(imp, pre_as_word)
            add_source(AS, source, policy, policylist, tuple_index)


def policy_analysis(policy):
    i = 0
    policylist = set()
    while policy[i] != "accept" and policy[i] != "announce" and policy[i] != "import": i += 1
    if i + 1 == len(policy):
        policy = 'Error'
    if policy[i + 1] == "any" or "{0.0.0.0/" in policy[i + 1]:
        policy = 'A'
    else:
        i += 1
        while i < len(policy):
            if policy[i].strip().isnumeric():
                policylist.add("AS" + policy[i].upper())
            if policy[i].lower().startswith("as") and policy[i][2:].strip().isnumeric():
                policylist.add(policy[i].upper())
            if '#' in policy[i]:
                policy = policy[:i]
                continue
            if policy[i].lower().startswith("as"):
                policylist.add(policy[i].upper())
            i += 1
        policy = 'O'
    return policy, policylist


def extract_name(block, AS):
    global ASNames
    if "as-name:" not in block: return
    name = block.split("as-name:")[1].split("\n")[0].strip()
    if '#' in name:
        name = name.split('#')[0]
    if name.lower() == "unspecified": return
    ASNames[name] = ASNames.get(name, set())
    ASNames[name].add(AS)


for i in range(1, 62):
    with codecs.open(f"./../../Sources/{i}.db", encoding='ISO-8859-1') as file:
        print(f'{i}:', time.time() - st)
        if file is None: continue
        block_list = file.read().split("\n\n")
        for block in block_list:
            if not block.startswith("aut-num:") and not block.startswith("*xx-num:"): continue
            block += "\n"
            key = extract_key(block)
            date_init(block, key)


for i in range(1, 62):
    with codecs.open(f"./../../Sources/{i}.db", encoding='ISO-8859-1') as file:
        print(f'{i}:', time.time() - st)
        if file is None: continue
        block_list = file.read().split("\n\n")
        for block in block_list:
            if not block.startswith("aut-num:") and not block.startswith("*xx-num:"): continue
            block += "\n"
            AS = extract_key(block)
            date = dateDict.get(AS, 0)
            if date != 0 and str(date) not in block and\
                str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:] not in block: continue
            extract_name(block, AS)
            AS_analysis(block, 'import:', AS)
            AS_analysis(block, 'export:', AS)

count = 0
print(ASDict)
for AS in ASDict.keys():
    if len(ASDict[AS][0].keys()) == 0:
        count += 1
print(count)
print(len(list(ASDict.keys())))
with open("./../../Pickles/DateDict.pickle", "wb") as p:
    pickle.dump(dateDict, p)
with open("./../../Pickles/Names.pickle", "wb") as p:
    pickle.dump(ASNames, p)
with open("./../../Pickles/ASDict.pickle", "wb") as p:
    pickle.dump(ASDict, p)

