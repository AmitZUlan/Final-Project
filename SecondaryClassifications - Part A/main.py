import pickle
import codecs
import re
import time

words = list()
st = time.time()
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:"


def extract_key(AS):
    key = "AS" + (AS.lower().split("as")[1]).split("\n")[0].strip()
    if '#' in key:
        key = key.split('#')[0]
    return key


def block_analysis(block, AS):
    TruthDict[AS] = [False, False]
    remark_list = block.split('remarks:')[1:]
    if not remark_list: return  # remark_list == []
    remark_analysis(AS, remark_list)


def remark_analysis(AS, remark_list):
    global remark_blocks
    if len(remark_list) == 1:
        header = remark_list[0].split("\n")[0].strip()
        data = remark_list[0][len(header):].strip()
        remark_blocks += [(header, data, AS)]
    elif len(remark_list) != 0:
        header = ""
        for i in range(len(remark_list)):
            if remark_list[i][-1] == '\n' and '\n' not in remark_list[i][:-1]:
                header += remark_list[i].strip() + '\n'
            else:
                offset = remark_list[i].find('\n')
                header += remark_list[i][:offset].strip()
                data = remark_list[i][offset:].strip()
                remark_blocks += [(header, data, AS)]
                header = ""


def import_analysis(imp, delim):
    global MemDict, IRR
    if "ipv6" in imp.lower():
        return None
    if ' afi ' in imp.lower() and 'ipv4' not in imp.lower() and ' any.' not in imp.lower():
        return None
    if delim in imp.lower():
        source = imp.lower().split(delim)[1]
    source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", source.strip())
    source = [s for s in source if s != '']
    if not source: return None
    policy = source
    source = source[0]
    if source.isnumeric():
        source = "AS" + source
    if source == "as":
        source += '' if policy[1].isnumeric() else '-'
        source += policy[1]
    if '#' in source:
        source = source.split('#')[0]
    source = source.upper()
    return source


def create_header(initial_header):
    global current_remark
    header = initial_header.strip()
    if "end" in header:
        header = header.split("end")[-1]
        current_remark = ""
    if ".com" in header:
        header = header.split(".com")[-1]
    while "peeringdb" in header:
        header = header.replace("peeringdb", "")
    while "peer-group:" in header:
        header = header.replace("peer-group:", "")
    return header


def add_entry(block, AS1, tor, is_export=False):
    global IRR, MemDict, relevant_remarks, current_header
    delim_remove = 'export:' if is_export else 'import:'
    source_delim = 'to ' if is_export else 'from '
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for field in (rem.split(delim_remove))[1:]:
            source = import_analysis(field, source_delim)
            if source is None: continue
            source = [source] if source[:2].lower() == 'as' and source[2:].isnumeric() else MemDict[source]
            for AS2 in source:
                AS2 = AS2.upper()
                if (AS1, AS2) in IRR.keys() and IRR[(AS1, AS2)] != tor:
                    continue
                IRR[(AS1, AS2)] = tor
                relevant_remarks[current_header] = relevant_remarks.get(current_header, dict())
                relevant_remarks[current_header][(AS1, AS2)] = tor


with open("./../../Pickles/Mem.pickle", "rb") as p:
    MemDict = pickle.load(p)
with open("./../../Pickles/DateDict.pickle", "rb") as p:
    DateDict = pickle.load(p)
remark_blocks = list()
customer = ["customer", "client", "downstream", "downlink"]
provider = ["provider", "upstream", "uplink"]
TruthDict = dict()
IRR = dict()
relevant_remarks = dict()

for i in range(1, 62):
    with codecs.open(f"./../../Sources/{i}.db", encoding='ISO-8859-1') as file:
        print(f'{i}:', time.time() - st)
        if file is None: continue
        blocks = file.read().split("\n\n")
        for block in blocks:
            block += "\n"
            if not block.startswith("aut-num:") and not block.startswith("*xx-num:"): continue
            AS = extract_key(block)
            date = DateDict.get(AS, 0)
            if date != 0 and str(date) not in block and\
                str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:] not in block: continue
            if 'remarks:' not in block: continue
            if 'import:' not in block and 'export:' not in block: continue
            block_analysis(block, AS)

currentAS = remark_blocks[0][2]
current_remark = ""
current_header = ""
for initial_header, block, AS in remark_blocks:
    if currentAS != AS:
        current_remark = ""
        current_header = create_header(initial_header.lower())
    currentAS = AS
    header = create_header(initial_header.lower())
    current_remark = "" if "peer" in header else current_remark
    current_header = create_header(initial_header.lower()) if "peer" in header else current_header
    current_remark = "provider" if any(word in header for word in provider) else current_remark
    TruthDict[currentAS][0] = True if any(word in header for word in provider) else TruthDict[currentAS][0]
    current_header = header if any(word in header for word in provider) else current_header
    current_remark = "customer" if any(word in header for word in customer) else current_remark
    TruthDict[currentAS][1] = True if any(word in header for word in customer) else TruthDict[currentAS][1]
    current_header = header if any(word in header for word in customer) else current_header
    if 'ipv6' in header.lower(): continue
    if current_remark != "provider" and current_remark != "customer": continue
    tor = 'C2P' if current_remark == "provider" else 'P2C'
    add_entry(block, AS.upper(), tor)
    add_entry(block, AS.upper(), tor, is_export=True)


current_remark = False
currentAS = remark_blocks[0][2]
current_header = ""
for initial_header, block, AS in remark_blocks:
    if not TruthDict[AS][0] or not TruthDict[AS][1]: continue
    if currentAS != AS:
        current_remark = False
        current_header = create_header(initial_header.lower())
    currentAS = AS
    header = create_header(initial_header.lower())
    current_remark = False if current_remark == '' else current_remark
    current_header = header if current_remark == '' else current_header
    current_remark = True if "peer" in header.lower() else current_remark
    current_header = header if "peer" in header.lower() else current_header
    current_remark = False if any(word in header for word in (provider + customer)) else current_remark
    if 'ipv6' in header.lower(): continue
    if not current_remark: continue
    add_entry(block, AS.upper(), 'P2P')
    add_entry(block, AS.upper(), 'P2P', is_export=True)

print(IRR)
print("P2P Value is:", list(IRR.values()).count("P2P"))
print("P2C Value is:", list(IRR.values()).count("P2C"))
print("C2P Value is:", list(IRR.values()).count("C2P"))
with open("./../../Pickles/IRRv2.pickle", "wb") as p:
    pickle.dump(IRR, p)
with open("./../../Pickles/Remarks Relevant to Remarks Heuristic.pickle", "wb") as p:
    pickle.dump(relevant_remarks, p)

