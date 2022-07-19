import pickle


with open(f"../Pickles/Siblings/MailDict.pickle", "rb") as p:
    MailDict = pickle.load(p)
with open(f"../Pickles/Siblings/OrgDict.pickle", "rb") as p:
    OrgDict = pickle.load(p)
with open(f"../Pickles/Siblings/MNTDict.pickle", "rb") as p:
    MNTDict = pickle.load(p)
with open(f"../Pickles/Siblings/AdminDict.pickle", "rb") as p:
    AdminDict = pickle.load(p)
with open(f"../Pickles/Siblings/techDict.pickle", "rb") as p:
    techDict = pickle.load(p)
with open(f"../Pickles/Siblings/notifyDict.pickle", "rb") as p:
    notifyDict = pickle.load(p)
with open(f"../Pickles/Siblings/NamesDict.pickle", "rb") as p:
    NamesDict = pickle.load(p)
with open(f"../Pickles/Siblings/MNTDict by AS.pickle", "rb") as p:
    MNT_AS_Dict = pickle.load(p)
with open(f"../Pickles/Siblings/Sets Siblings.pickle", "rb") as p:
    sets_AS_Dict = pickle.load(p)


def concat_siblings(AS_Siblings):
    global siblingDict
    for AS, sibling_indicator in AS_Siblings.items():
        sibling_set = set()
        sibling_set.update(*sibling_indicator.values())
        for sibling in sibling_set:
            comment = [indicator for indicator in sibling_indicator.keys() if sibling in sibling_indicator[indicator]]
            comment = ', '.join(comment)
            siblingDict[(AS, sibling)] = ('S2S', comment)


def sibling_insertion(AS_Siblings, source_dict, field, max_len=10**9,
                      forbidden_list={'dum', 'yahoo', 'aol.com', 'hotmail', 'live.com', 'outlook.com'}):
    for key in source_dict.keys():
        if len(source_dict[key]) < 2 or max_len < len(source_dict[key])\
                or any([word in key.lower() for word in forbidden_list]):
            continue
        for AS in source_dict[key]:
            AS_Siblings[AS] = AS_Siblings.get(AS, dict())
            siblings_list = source_dict[key].copy()
            siblings_list.remove(AS)
            AS_Siblings[AS][f"{field}={key}"] = siblings_list
