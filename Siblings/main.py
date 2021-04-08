import pickle
import codecs
import re
import time
from os import path
import csv

path = path.abspath(path.dirname(__file__))
MailDict = {}
siblingDict = {}
delim_import = "mntner:|descr:|admin-c:|tech-c:|upd-to:|auth:|mnt-by:|source:|mnt-nfy:|notify:|person:|address:|phone:|fax-no:|e-mail:|nic-hdl:|remarks:|route:|origin:|aut-num:|as-name:|export:|default:|inet-rtr:|local-as:|ifaddr:|peer:|rs-in:|rs-out:|member-of:|as-set:|members:|peering-set:|peering:|route-set:|mbrs-by-ref:|alias:|route6:|key-cert:|method:|owner:|fingerpr:|certif:|role:|trouble:|mnt-lower:|created:|last-modified:|members-by-ref:|mnt-routes:|inject:|components:|aggr-mtd:|holes:|country:|Mnt-by:|Changed:|as-block:|inet6num:|netname:|status:|org:|inetnum:|interface:|mp-peer:|referral-by:|organisation:|org-name:|org-type:|mnt-ref:|rtr-set:|limerick:|text:|author:|filter:|import:"
st = time.time()

f = [None] * 61
for i in range(61):
    f[i] = codecs.open(path + "/../sources/" + str(i + 1) + ".db", encoding='ISO-8859-1')
global ASDict
for file in f:

    print(time.time() - st)

    if file is not None:
        siblingread = file.read().split("\n\n")

        for block in siblingread:

            block = block + "\n"

            for AS in (block.split("aut-num:"))[1:]:

                key = "AS" + (AS.lower().split("as")[1]).split("\n")[0]

                if '#' in key:
                    key = key.split('#')[0]

                if "changed:" in AS:
                    sib = (AS.split("changed:"))[1]
                    sib = (sib.split('\n'))[0].strip()

                    if '@' not in sib:
                        continue

                    searchsib = (sib.split('@')[1]).split(' ')[0]

                    if searchsib not in MailDict.keys():
                        MailDict[searchsib] = []

                    MailDict[searchsib].append(key)

for key in MailDict.keys():
    if len(MailDict[key]) < 2:
        continue
    for value in MailDict[key]:
        HisSiblings = MailDict[key].copy()
        HisSiblings.remove(value)
        for sibling in HisSiblings:
            siblingDict[(value, sibling)] = ["S2S", key]


print(siblingDict)

with open(path + "/../Pickles/SiblingsDict.pickle", "wb") as p:
    pickle.dump(siblingDict, p)


# with open('RefCompare.csv', mode='w', newline='') as f:
#     fwrite = csv.writer(f, delimiter=',')
#     fwrite.writerow(['AS1', 'AS2', 'IRR Prediction', 'Caida Prediction', ' '] * 50)
#     w = []
#     i = 0
#     for k in Ref.keys():
#         i = i + 1
#         if k in IRR.keys():
#             w = w + [k[0], k[1], IRR[k], Ref[k], ' ']
#         else:
#             w = w + [k[0], k[1], "Doesn't Exist", Ref[k], ' ']
#         if i == 50:
#             fwrite.writerow(w)
#             w = []
#             i = 0
#     for k in (list(set(list(Ref.keys()) + list(IRR.keys())) - set(Ref.keys()))):
#         i = i + 1
#         w = w + [k[0], k[1], IRR[k], "Doesn't Exist", ' ']
#         if i == 50:
#             fwrite.writerow(w)
#             w = []
#             i = 0
#     if i != 0:
#         fwrite.writerow(w)
