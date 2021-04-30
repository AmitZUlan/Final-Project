import pickle
import codecs
import re
import time
from os import path
words = []
st = time.time()
path = path.abspath(path.dirname(__file__))
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:"


def extract_key(AS):
    key = "AS" + (AS.lower().split("as")[1]).split("\n")[0]
    if '#' in key:
        key = key.split('#')[0]
    return key


def block_analysis(block, delim_remove):
    if not block.startswith("aut-num:"):
        return
    AS = extract_key(block)
    if AS in DateDict.keys() and DateDict[AS] != 0 and str(DateDict[AS]) not in block:
        return
    if AS not in TruthDict.keys():
        TruthDict[AS] = [False, False]
    remark_list = (block.split(delim_remove))[1:]
    if not remark_list: return
    remark_analysis(AS, remark_list)


def remark_analysis(AS, remark_list):
    global remark_blocks
    if len(remark_list) == 1:
        header = remark_list[0].split("\n")[0]
        data = remark_list[0][len(header) + 1:]
        remark_blocks += [(header, data, AS)]
    elif len(remark_list) != 0:
        header = ""
        for i in range(len(remark_list)):
            if remark_list[i][-1] == '\n' and '\n' not in remark_list[i][:-1]:
                header += remark_list[i]
            else:
                header += remark_list[i].split('\n')[0]
                offset = len(header) + 1
                data = remark_list[i][offset:]
                remark_blocks += [(header, data, AS)]
                header = ""


def block_list_analysis(block_list, delim_remove):
    for block in block_list:
        block = block + "\n"
        block_analysis(block, delim_remove)


def import_analysis(imp, delim):
    global MemDict, IRR
    if "ipv6" in imp.lower():
        return None
    if delim in imp.lower():
        imp = imp.lower().split(delim)[1]
    source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", imp.lower())
    while "" in source: source.remove("")
    if not source:
        return None
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
    return source


def create_header(initial_header):
    global current_remark
    header = initial_header
    if "end" in header:
        header = header.split("end")[-1]
        current_remark = ""
    if ".com" in header:
        header = header.split(".com")[-1]
    while "peer-group:" in header:
        header = header.replace("peer-group:", "")
    return header


with open(path + "\..\Pickles\Mem.pickle", "rb") as p:
    MemDict = pickle.load(p)
with open(path + "\..\Pickles\DateDict.pickle", "rb") as p:
    DateDict = pickle.load(p)
remark_blocks = list()
customer = ["customer", "client", "downstream", "downlink"]
provider = ["provider", "upstream", "uplink"]
TruthDict = dict()
IRR = dict()

f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../Sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
for file in f:
    print(time.time() - st)
    if file is not None:
        blocks = file.read().split("\n\n")
        block_list_analysis(blocks, "remarks:")

currentAS = remark_blocks[0][2]
current_remark = ""
for tup in remark_blocks:
    AS = tup[2]
    remarks = tup[:-1]
    if currentAS != AS:
        current_remark = ""
    currentAS = AS
    header = create_header(remarks[0].lower())
    for word in provider:
        if word in header.lower():
            current_remark = "provider"
            TruthDict[currentAS][0] = True
            break
    for word in customer:
        if word in header.lower():
            current_remark = "customer"
            TruthDict[currentAS][1] = True
            break
    block = remarks[1]
    if current_remark == "":
        continue
    delim_remove = 'import:'
    AS1 = AS.upper()
    for exp in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for imp in (exp.split(delim_remove))[1:]:
            source = import_analysis(imp, 'from ')
            if source is None: continue
            for AS2 in MemDict[source]:
                AS2 = AS2.upper()
                if current_remark == "provider":
                    IRR[(AS1, AS2)] = 'C2P'
                if current_remark == "customer":
                    IRR[(AS1, AS2)] = 'P2C'

current_remark = False
currentAS = remark_blocks[0][2]
for tup in remark_blocks:
    AS = tup[2]
    remarks = tup[:-1]
    if currentAS != AS:
        current_remark = False
    currentAS = AS
    header = create_header(remarks[0].lower())
    if not TruthDict[currentAS][0] or not TruthDict[currentAS][1]:
        continue
    if "peer" in header.lower():
        current_remark = True
    for word in provider:
        if word in header.lower():
            current_remark = False
            break
    for word in customer:
        if word in header.lower():
            current_remark = False
            break
    block = remarks[1]
    if not current_remark:
        continue
    delim_remove = 'import:'
    AS1 = AS.upper()
    for exp in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for imp in (exp.split(delim_remove))[1:]:
            source = import_analysis(imp, 'from ')
            if source is None: continue
            for AS2 in MemDict[source]:
                AS2 = AS2.upper()
                if current_remark:
                    IRR[(AS1, AS2)] = 'P2P'

print(IRR)
print("P2P Value is:", list(IRR.values()).count("P2P"))
print("P2C Value is:", list(IRR.values()).count("P2C"))
print("C2P Value is:", list(IRR.values()).count("C2P"))
with open(path + "\..\Pickles\IRRv2.pickle", "wb") as p:
    pickle.dump(IRR, p)

