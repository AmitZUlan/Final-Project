import pickle
import codecs
import re
import time
from os import path
words = []
st = time.time()
path = path.abspath(path.dirname(__file__))
delim_import = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:"
delim_export = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|import:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:"
# with open(path + "\..\Pickles\IRR.pickle", "rb") as p:
#     IRR = pickle.load(p)
with open(path + "\..\Pickles\Mem.pickle", "rb") as p:
    MemDict = pickle.load(p)
remark_blocks = []
customer = ["customer", "client", "downstream", "downlink"]
provider = ["provider", "upstream", "uplink"]
TruthDict = {}


IRR = {}

f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../Sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
for file in f:
    print(time.time() - st)
    if file is not None:
        blocks = file.read().split("\n\n")
        for block in blocks:
            block += '\n'
            if block.startswith("aut-num:"):
                AS1 = block.split("aut-num:")[1].split("\n")[0].strip()
                if AS1 not in TruthDict.keys():
                    TruthDict[AS1] = [False, False]
                remark_split = block.split("remarks:")[1:]
                if len(remark_split) == 1:
                    header = remark_split[0].split("\n")[0]
                    data = remark_split[0][len(header) + 1:]
                    remark_blocks.append((header, data, AS1))
                elif len(remark_split) != 0:
                    header = ""
                    for i in range(len(remark_split)):
                        if remark_split[i][-1] == '\n' and '\n' not in remark_split[i][:-1]:
                            header += remark_split[i]
                        else:
                            header += remark_split[i].split('\n')[0]
                            offset = len(remark_split[i].split('\n')[0]) + 1
                            data = remark_split[i][offset:]
                            remark_blocks.append((header, data, AS1))
                            header = ""

currentAS = remark_blocks[0][2]
currentremark = ""
for i in range(len(remark_blocks)):
    if currentAS != remark_blocks[i][2]:
        currentremark = ""
    currentAS = remark_blocks[i][2]
    header = remark_blocks[i][0].lower()
    if "end" in remark_blocks[i][0]:
        header = header.split("end")[-1]
        currentremark = ""
    if ".com" in header:
        header = header.split(".com")[-1]
    while "peer-group:" in header:
        header = header.replace("peer-group:", "")
    for word in provider:
        if word in header.lower():
            currentremark = "provider"
            TruthDict[currentAS][0] = True
            break
    for word in customer:
        if word in header.lower():
            currentremark = "customer"
            TruthDict[currentAS][1] = True
            break
    AS1 = remark_blocks[i][2]
    block = remark_blocks[i][1]
    if currentremark == "":
        continue
    for exp in (re.split(delim_import, block.lower())):
        for imp in (exp.split("import:"))[1:]:
            if "ipv6" in imp.lower():
                continue
            if "from " in imp.lower():
                source = imp.lower().split("from ")[1]
            source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", source)
            while "" in source: source.remove("")
            if not source:
                continue
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
            for AS2 in MemDict[source]:
                AS1 = AS1.upper()
                AS2 = AS2.upper()
                if currentremark == "provider":
                    IRR[(AS1, AS2)] = 'C2P'
                if currentremark == "customer":
                    IRR[(AS1, AS2)] = 'P2C'
    # for imp in (re.split(delim_export, block.lower())): # maybe need to remove
    #     for exp in (imp.split("export:"))[1:]:
    #         if "ipv6" in exp.lower(): #check this with tal
    #             continue
    #         if "to " in exp.lower():
    #             source = exp.lower().split("to ")[1]
    #         source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", source)
    #         while "" in source: source.remove("")
    #         if not source:
    #             continue
    #         policy = source
    #         source = source[0]
    #         if source.isnumeric():
    #             source = "AS" + source
    #         if source == "as":
    #             if policy[1].isnumeric():
    #                 source = source + policy[1]
    #             else:
    #                 source = source + '-' + policy[1]
    #         if '#' in source:
    #             source = source.split('#')[0]
    #         source = source.upper()
    #         for AS2 in MemDict[source]:
    #             AS1 = AS1.upper()
    #             AS2 = AS2.upper()
    #             if currentremark == "provider":
    #                 IRR[(AS2, AS1)] = 'P2C'
    #                 IRR[(AS1, AS2)] = 'C2P'
    #             if currentremark == "customer":
    #                 IRR[(AS2, AS1)] = 'C2P'
    #                 IRR[(AS1, AS2)] = 'P2C'
currentAS = remark_blocks[0][2]
currentremark = False
for i in range(len(remark_blocks)):
    if currentAS != remark_blocks[i][2]:
        currentremark = False
    currentAS = remark_blocks[i][2]
    header = remark_blocks[i][0].lower()
    if "end" in remark_blocks[i][0]:
        header = header.split("end")[-1]
        currentremark = False
    if ".com" in header:
        header = header.split(".com")[-1]
    while "peer-group:" in header:
        header = header.replace("peer-group:", "")
    if not TruthDict[currentAS][0] or not TruthDict[currentAS][1]:
        continue
    if "peer" in header.lower():
        currentremark = True
    for word in provider:
        if word in header.lower():
            currentremark = False
            break
    for word in customer:
        if word in header.lower():
            currentremark = False
            break
    AS1 = remark_blocks[i][2]
    block = remark_blocks[i][1]
    if not currentremark:
        continue
    for exp in (re.split(delim_import, block.lower())):
        for imp in (exp.split("import:"))[1:]:
            if "ipv6" in imp.lower():
                continue
            if "from " in imp.lower():
                source = imp.lower().split("from ")[1]
            source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", source)
            while "" in source: source.remove("")
            if not source:
                continue
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
            for AS2 in MemDict[source]:
                AS1 = AS1.upper()
                AS2 = AS2.upper()
                if currentremark:
                    IRR[(AS1, AS2)] = 'P2P'
    # for imp in (re.split(delim_export, block.lower())): # maybe need to remove
    #     for exp in (imp.split("export:"))[1:]:
    #         if "ipv6" in exp.lower(): #check this with tal
    #             continue
    #         if "to " in exp.lower():
    #             source = exp.lower().split("to ")[1]
    #         source = re.split(" |\t|\n|\;|\<|\>|\$|\^|\+", source)
    #         while "" in source: source.remove("")
    #         if not source:
    #             continue
    #         policy = source
    #         source = source[0]
    #         if source.isnumeric():
    #             source = "AS" + source
    #         if source == "as":
    #             if policy[1].isnumeric():
    #                 source = source + policy[1]
    #             else:
    #                 source = source + '-' + policy[1]
    #         if '#' in source:
    #             source = source.split('#')[0]
    #         source = source.upper()
    #         for AS2 in MemDict[source]:
    #             AS1 = AS1.upper()
    #             AS2 = AS2.upper()
    #             if currentremark:
    #                 IRR[(AS2, AS1)] = 'P2P'
    #                 IRR[(AS1, AS2)] = 'P2P'


print(IRR)
with open(path + "\..\Pickles\IRRv2.pickle", "wb") as p:
    pickle.dump(IRR, p)

