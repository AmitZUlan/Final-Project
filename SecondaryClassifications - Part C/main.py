import pickle
import codecs
import re
from os import path

path = path.abspath(path.dirname(__file__))
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|import:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|import:|peering-set:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:"
customer = ["customer", "client", "downstream", "downlink"]
provider = ["provider", "upstream", "uplink"]
IRR = {}


def swap(NamesDict, SetsDict, name, MemDict, namelist):
    retval = []
    if name in MemDict.keys():
        return MemDict[name]
    if name.startswith("AS") and name[2:].isnumeric():
        retval.append(name)
        MemDict[name] = retval
        return retval
    # if name.startswith("AS") and name[2] == '-' and name[3:].isnumeric():
    #     retval.append(name[:2] + name[3:])
    #     MemDict[name] = retval
    #     return retval
    if name in namelist:
        return []
    if name in NamesDict.keys():
        retval.append(NamesDict[name])
    elif name in SetsDict.keys():
        for v in SetsDict[name]:
            if v != name:
                namelist.append(name)
                newretval = swap(NamesDict, SetsDict, v, MemDict, namelist)
                namelist.remove(name)
                retval = list(set(retval + newretval))
            else:
                SetsDict[name].remove(name)
    elif name.startswith("AS") and name[2] == '-' and name[3:].isnumeric():
        retval.append(name[:2] + name[3:])
        MemDict[name] = retval
        return retval
    else:
        for key, v in NamesDict.items():
            if ':' not in name and (len(name) > 2 and name in key or (name.startswith("AS") and name[2:] in key and name.lower()[2:] not in "as" and name.lower()[2:] not in "asn" and len(name) > 4) or (name.startswith("AS-") and name[3:] in key and name.lower()[3:] not in "as" and name.lower()[3:] not in "asn" and len(name) > 5)):
                retval.append(v)
            MemDict[name] = retval
            return retval
        retval.append(name)
    MemDict[name] = retval
    return retval


with open(path + "\..\Pickles\Mem.pickle", "rb") as p:
    MemDict = pickle.load(p)
with open(path + "\..\Pickles\Sets.pickle", "rb") as p:
    SetsDict = pickle.load(p)
with open(path + "\..\Pickles\\Names.pickle", "rb") as p:
    NamesDict = pickle.load(p)

f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../Sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
for file in f:
    if file is not None:
        for block in file.read().split("\n\n"):
            block1 = block
            block = block.lower()
            iscustomer = False
            isprovider = False
            if block.startswith("peering-set:"):
                peeringset = block.split("peering-set:")[1]
                peeringset = (peeringset.split("\n")[0]).strip()
                description = None
                if "desc:" in block:
                    description = block.split("desc:")[1]
                    description = re.split(delim + "|peering:", description)[0]
                for cust in customer:
                    if cust in peeringset:
                        iscustomer = True
                        break
                for prov in provider:
                    if prov in peeringset:
                        isprovider = True
                        break
                if description != None and not isprovider and not iscustomer:
                    for cust in customer:
                        if cust in description:
                            iscustomer = True
                            break
                    for prov in provider:
                        if prov in description:
                            isprovider = True
                            break
                if (not iscustomer and not isprovider) or (iscustomer and isprovider):
                    continue
                setname = ((block.split("peering-set:")[1]).split("\n")[0]).strip()
                if '#' in setname:
                    setname = setname.split("#")[0]
                if "as" not in setname:
                    continue
                AS1 = setname.split("as")[1]
                AS1 = "AS" + re.split(":|-", AS1)[0]
                if AS1 == "AS":
                    continue
                if not AS1[2:].isnumeric():
                    continue
                members = block1.split("peering:")[1:]
                for member in members:
                    member = re.split(delim, member)[0]
                    if "as" not in member.lower():
                        continue
                    i = 0
                    while member[i].lower() != 'a' or member[i + 1].lower() != 's': i += 1
                    member = ((member[i:]).split("\n")[0]).split(" ")[0].strip()
                    for AS2 in swap(NamesDict, SetsDict, member, MemDict, []):
                        if AS1 == AS2:
                            continue
                        if iscustomer and not isprovider:
                            IRR[(AS1, AS2)] = "P2C"
                        if not iscustomer and isprovider:
                            IRR[(AS1, AS2)] = "C2P"

print(IRR)
with open(path + "/../Pickles/IRRv4.pickle", "wb") as p:
    pickle.dump(IRR, p)
