import pickle
import codecs
import re
from os import path

path = path.abspath(path.dirname(__file__))
ASSets = {}
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|import:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|import:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:"


def solve_name(name):
    if ":" not in name and "-" not in name:
        return name
    names = re.split(":|-")
    for nm in names:
        if nm.lower().startswith("as") and nm.lower().split("as")[1].isnumeric():
            return nm.upper()
        if nm.isnumeric():
            return "AS" + nm


def block_analysis(block):
    global ASSets
    if not block.startswith("as-set:"):
        return
    set_name = ((block.split("as-set:")[1]).split("\n")[0]).strip()
    if '#' in set_name:
        set_name = set_name.split("#")[0]
    if set_name not in ASSets.keys():
        ASSets[set_name] = []
    members = set_member_extraction(block)
    if members:
        ASSets[set_name] = ASSets[set_name] + members


def set_member_extraction(block):
    members = []
    for member in block.split("members:")[1:]:
        member = re.split(delim, member)[0]
        for m in (member.split(",\n ")[:-1]):
            m = m.split("\n")[0]
            membersline = re.split(" |,", m)
            while "" in membersline: membersline.remove("")
            for mem in membersline:
                if mem.startswith("#"): break
                members.append(mem.strip())
        m = (member.split("\n ")[-1]).split("\n")[0]
        membersline = re.split(" |,", m)
        while "" in membersline: membersline.remove("")
        for mem in membersline:
            if mem.startswith("#"):
                break
            members.append(mem.strip())
    return members


f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../Sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
for file in f:
    if file is not None:
        for block in file.read().split("\n\n"):
            block += '\n'
            block_analysis(block)


with open(path + "/../Pickles/Sets.pickle", "wb") as p:
    pickle.dump(ASSets, p)
