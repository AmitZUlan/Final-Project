import pickle
from os import path
import matplotlib.pyplot as plt
import numpy as np


# for msg in ['I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary']:
#     with open(f'./../../Pickles/{msg} Mistakes.pickle', 'rb') as p:
#         mistakes = pickle.load(p)
#     x = [i for i in range(100)]
#     y = [list(mistakes.values()).count(xi) for xi in x]
#     plt.plot(x, y)
#     plt.grid()
#     plt.yticks([int(max(y)/50) * i for i in range(50)])
#     plt.xlabel('# of Mistakes')
#     plt.ylabel('Count of ASNs with x Mistakes')
#     plt.suptitle('Mistakes Histogram')
#     plt.show()


def plot_result_list(result_list, with_respect_to_ToRs, msg, max_threshold=10**8, isDate=False):
    assert len(result_list[1]) == 101 or isDate
    y = [round(result_list[2][i]/result_list[1][i], 2) for i in range(len(result_list[1])) if i < max_threshold]
    x = [round(result_list[1][i]/result_list[1][-1], 2) for i in range(len(result_list[1])) if i < max_threshold]
    temp_dict = dict()
    for i in range(len(y)):
        temp_dict[y[i]] = x[i]
    y, x = zip(*temp_dict.items())
    plt.scatter(x, y)
    for xi, yi in zip(x, y):
        label = f"({xi}, {yi})"
        plt.annotate(label,
                     (xi, yi),
                     textcoords="offset points",
                     xytext=(0, 10),
                     ha='center',
                     )
    plt.suptitle(msg)
    plt.xlabel('Coverage')
    plt.ylabel('Confidence')
    if isDate:
        plt.savefig(f"./../../Example Files/Plots/Confidence vs. Coverage/{msg} Earliest Date='None'.png", dpi=300)
    else:
        plt.savefig(f"./../../Example Files/Plots/Confidence vs. Coverage/{msg} with respect to {with_respect_to_ToRs} ToRs, max_threshold={max_threshold - 1}.png", dpi=300)
    plt.close()


# for msg in ['I_E Dictionary', 'Remarks Dictionary']:
#     result_list = list()
#     for date_threshold in range(2020 * 10 ** 4, 1950 * 10 ** 4, -10 ** 4):
#         if not path.exists(f'./../../Pickles/Dates/{msg}/Oldest Date={date_threshold}.pickle'): continue
#         with open(f'./../../Pickles/Dates/{msg}/Oldest Date={date_threshold}.pickle', 'rb') as p:
#             result_list += pickle.load(p)
#     assert result_list != list()
#     result_list = list(zip(*result_list))
#     plot_result_list(result_list, None, msg, isDate=True)


for msg in ['I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary']:
    result_list_2_sided = list()
    result_list = list()
    for mistake_threshold in range(101):
        if not path.exists(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold is {mistake_threshold}%.pickle'): continue
        with open(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold is {mistake_threshold}%.pickle', 'rb') as p:
            temp_result = pickle.load(p)
            result_list_2_sided += [temp_result[0]]
            result_list += [temp_result[1]]
    assert result_list != list()
    result_list = list(zip(*result_list))
    result_list_2_sided = list(zip(*result_list_2_sided))

    plot_result_list(result_list_2_sided, '2-Sided', msg, 41)
    plot_result_list(result_list, 'Overall', msg, 41)
    plot_result_list(result_list_2_sided, '2-Sided', msg, 101)
    plot_result_list(result_list, 'Overall', msg, 101)



