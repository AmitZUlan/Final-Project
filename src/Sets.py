import os
import pickle
import codecs
import time
import re

st = time.time()
ASSets = dict()
dateDict = dict()
delim = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|changed:|source:|mnt-nfy:|notify:|person:|address" \
        ":|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local" \
        "-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref" \
        ":|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified" \
        ":|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block" \
        ":|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type" \
        ":|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import: "


def extract_setname(block):
    global ASSets
    set_name = ((block.split("as-set:")[1]).split("\n")[0]).strip()
    if '#' in set_name:
        set_name = set_name.split("#")[0]
    return set_name


def block_analysis(block, set_name):
    global ASSets
    ASSets[set_name] = list() if set_name not in ASSets.keys() else ASSets[set_name]
    members = set_member_extraction(block)
    if not members: return
    ASSets[set_name] += members


def set_member_extraction(block):
    members = list()
    delim_remove = 'members:'
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block)):
        for field in (rem.split(delim_remove))[1:]:
            members = re.split(' |,|\n', field.strip())
    members = [member for member in members if member != '']
    return members


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
            if key in dateDict.keys():
                if dateDict[key] > date:
                    return
            dateDict[key] = date
    delim_remove = 'last-modified:'
    for rem in (re.split(delim.replace("|" + delim_remove, ''), block.lower())):
        for field in (rem.split(delim_remove))[1:]:
            date = field.split('t')[0].strip()
            date = date.split('-')
            date = ''.join(date)
            date = int(date) if date.isnumeric() else 0
            if key in dateDict.keys():
                if dateDict[key] > date:
                    return
            dateDict[key] = date


def main():
    length = len(os.listdir('../Sources'))
    print(length)
    for i in range(length):
        with codecs.open(f"../Sources/{i}.db", encoding='ISO-8859-1') as file:
            print(f'{i}:', time.time() - st)
            if file is None: continue
            block_list = file.read().split("\n\n")
            for block in block_list:
                block += '\n'
                if not block.startswith("as-set:"): continue
                set_name = extract_setname(block)
                date_init(block, set_name)
            for block in block_list:
                block += '\n'
                if not block.startswith("as-set:"): continue
                set_name = extract_setname(block)
                date = dateDict.get(set_name, 0)
                if date != 0 and str(date) not in block and\
                    str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:] not in block: continue
                block_analysis(block, set_name)

    with open("../Pickles/Sets DateDict.pickle", "wb") as p:
        pickle.dump(dateDict, p)

    with open("../Pickles/Sets.pickle", "wb") as p:
        pickle.dump(ASSets, p)
