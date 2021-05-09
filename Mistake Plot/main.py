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


for msg in ['I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary']:
    result_list_2_sided = list()
    result_list = list()
    for mistake_threshold in range(101):
        if not path.exists(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold {mistake_threshold}.pickle'): continue
        with open(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold {mistake_threshold}.pickle', 'rb') as p:
            temp_result = pickle.load(p)
            result_list_2_sided += [temp_result[0]]
            result_list += [temp_result[1]]
    result_list = list(zip(*result_list))
    result_list_2_sided = list(zip(*result_list_2_sided))
    two_sided_classifications = np.array(result_list[1])
    two_sided_agreements = np.array(result_list[2])
    y = [result_list_2_sided[2][i]/result_list_2_sided[1][i] for i in range(40)]
    x = [result_list_2_sided[1][i]/result_list_2_sided[1][-1] for i in range(40)]
    y2 = [round((y[i] - y[i + 1])/(x[i] - x[i + 1]), 4) for i in range(39)]
    y = [round(result_list_2_sided[2][i]/result_list_2_sided[1][i], 4) for i in range(40)]
    x = [round(result_list_2_sided[1][i]/result_list_2_sided[1][-1], 4) for i in range(40)]
    # y2 = [round(result_list[2][i]/result_list[1][i], 2) for i in range(40)]
    # x2 = [round(result_list[1][i]/result_list[1][-1], 2) for i in range(40)]
    plt.scatter(x, y)
    # plt.scatter(x2, y2)
    # plt.legend(['2-Sided', 'Overall'])
    plt.suptitle(msg)
    plt.xlabel('Coverage Ratio')
    plt.ylabel('Agreements Ratio')
    i = 1
    for xi, yi in zip(x, y):
        i *= -1
        label = f"({xi}, {yi})"
        plt.annotate(label,
                     (xi, yi),
                     textcoords="offset points",
                     xytext=(i * 50, -5),
                     ha='center',
                     # arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',
                     #                 color='k'),
                     )
    # for xi, yi in zip(x2, y2):
    #     label = f"({xi}, {yi})"
    #     plt.annotate(label,
    #                  (xi, yi),
    #                  textcoords="offset points",
    #                  xytext=(0, 10),
    #                  ha='center')
    plt.show()

    # fig, plots = plt.subplots(2, sharex=True)
    # plots[0].scatter(mistake_threshold, two_sided_classifications)
    # plots[1].scatter(mistake_threshold, two_sided_agreements)
    # fig.suptitle(msg)
    # plt.xticks(range(41))
    # plt.xlabel('Coverage Ratio')
    # plots[0].set_ylabel('2-Sided Agreements/2-Sided Classifications')
    # plots[1].set_ylabel('2-Sided Agreements/Classifications')
    # plt.show()

