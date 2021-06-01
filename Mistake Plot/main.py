import pickle
import matplotlib.pyplot as plt
import math

xlabels = {
    0: 'Overall Coverage [%]',
    1: '2-Sided Coverage [%]',
    3: 'AS Coverage [%]',
    4: 'AS Coverage (2-Sided Perspective) [%]',
    6: 'Overall Coverage (2-Sided Perspective) [%]'
}


def plot_result_list(initial_x_list, xlabel, initial_y_list, ylabel, msg, max_threshold, is_min_2_sided, legends, a=False):
    j = -1
    for initial_x, initial_y in zip(initial_x_list, initial_y_list):
        j += 1
        x = initial_x
        y = initial_y
        temp_dict = dict()
        for i in range(len(y)):
            temp_dict[y[i]] = (x[i], i)
        y = tuple(temp_dict.keys())
        x, i_list = zip(*temp_dict.values())
        if not is_min_2_sided and 10 not in i_list:
            x += (initial_x[10], )
            y += (initial_y[10], )
            i_list += (10, )
        plt.scatter(x, y)
        for xi, yi, ii in zip(x, y, i_list):
            label = f"{100 - ii}%" if not is_min_2_sided else f"{ii}"
            plt.annotate(
                label,
                (xi, yi),
                textcoords="offset points",
                xytext=(15 * math.cos((2 * (j == 2) + 1) * math.pi/2), -4 + 9 * math.sin((2 * (j == 2) + 1) * math.pi/2)),
                ha='center',
            )
    if legends:
        plt.legend(legends)
    plt.suptitle(msg)
    plt.grid()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    remove_index = msg.find('\nFull Coverage') - 1
    directory = msg[msg.find(', ') + 2:msg.find('\n')]
    replace_count = msg.count(', ') - len(initial_x_list) + 1
    msg = msg.replace(', ', '/', replace_count)
    msg = msg.replace('\n', ',')
    if a:
        mini = min(*(initial_y_list[0] + initial_y_list[1]))
        maxi = max(*(initial_y_list[0] + initial_y_list[1]))
        plt.yticks(list(range(mini, maxi + 1)))
        if is_min_2_sided:
            plt.savefig(f"./../../Example Files/Plots/Confidence vs. Coverage/{directory}/{msg[:remove_index]} "
                        f"{xlabel[:xlabel.find(' [%]')]}.png", dpi=400, bbox_inches='tight')
            print(f"Finished {directory} - {msg[:remove_index]} "
                  f"{xlabel[:xlabel.find(' [%]')]}")
        else:
            plt.savefig(f"./../../Example Files/Plots/Confidence vs. Coverage/{directory}/{msg[:remove_index]} "
                        f"{xlabel[:xlabel.find(' [%]')]}, max_threshold={max_threshold - 1}.png", dpi=400, bbox_inches='tight')
            print(f"Finished {directory} - {msg[:remove_index]} "
                  f"{xlabel[:xlabel.find(' [%]')]}, max_threshold={max_threshold - 1}")
    else:
        plt.savefig(f"./../../Example Files/Plots/Confidence vs. Coverage/{directory}/{msg[:remove_index]} "
                    f"{ylabel[:ylabel.find(' [%]')]}.png", dpi=400, bbox_inches='tight')
        print(f"Finished {directory} - {msg[:remove_index]} "
              f"{ylabel[:ylabel.find(' [%]')]}")

    plt.close()


def plot_result_lists(result_lists, bases, max_threshold, legend, msg, is_min_2_sided=False, ylabel='Agreements Ratio [%]\n(# of 2-Sided ToRs Agreements/# of 2-Sided ToRs)'):
    data_len = len(result_lists[0][0])
    y_list = [[round(100 * result_lists[j][2][i] / result_lists[j][1][i]) for i in range(min(data_len, max_threshold))] for j in range(len(result_lists))]
    for index, xlabel in xlabels.items():
        if isinstance(result_lists[0][index][0], int):
            x_list = [[round(100 * result_lists[j][index][i] / result_lists[0][index][-1]) for i in range(data_len)] for j in range(len(result_lists))]
        else:
            x_list = [[round(100 * len(result_lists[j][index][i]) / len(result_lists[0][index][-1])) for i in range(data_len)] for j in range(len(result_lists))]
        full_coverage = result_lists[0][index][-1] if isinstance(result_lists[0][index][-1], int) else len(result_lists[0][index][-1])

        plot_result_list(x_list, xlabel, y_list, ylabel, msg +
                         f', {legend}={", ".join(map(str, bases))}\nFull Coverage={full_coverage}'
                         , max_threshold, is_min_2_sided, legends=tuple(f'{legend}={base}' for base in bases), a=True)


for msg in ('I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary'):
    result_list0 = list()
    result_list3 = list()
    result_list5 = list()
    for mistake_threshold in range(101):
        with open(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold is {mistake_threshold}%.pickle', 'rb') as p:
            temp = pickle.load(p)
            result_list0 += [temp[0]]
            result_list3 += [temp[1]]
            result_list5 += [temp[2]]
    assert result_list0 != list()
    assert result_list5 != list()
    result_list0 = list(zip(*result_list0))
    result_list3 = list(zip(*result_list3))
    result_list5 = list(zip(*result_list5))
    for max_threshold in (41, 101):
        plot_result_lists((result_list0, result_list3, result_list5), (0, 3, 5), max_threshold, 'Base 2-Sided Threshold', msg)


for msg in ('I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary'):
    result_list0 = list()
    result_list90 = list()
    for min_2_sided in range(11):
        with open(f'./../../Pickles/2-Sides Requirement/{msg}/Requirement of at least '
                  f'{min_2_sided} 2-Sided ToRs.pickle', 'rb') as p:
            temp = pickle.load(p)
            result_list0 += [temp[0]]
            result_list90 += [temp[1]]
    assert result_list0 != list()
    assert result_list90 != list()
    result_list0 = result_list0[::-1]
    result_list90 = result_list90[::-1]
    result_list0 = list(zip(*result_list0))
    result_list90 = list(zip(*result_list90))
    result_lists = (result_list0, result_list90)
    bases = (0, 90)
    data_len = len(result_list0[0])
    legend = 'Base Agreements Ratio Threshold'
    plot_result_lists(result_lists, bases, data_len, legend, msg, True)

    for index, ylabel in xlabels.items():
        if isinstance(result_lists[0][index][0], int):
            y_list = (
                [round(100 * result_lists[0][index][i] / result_lists[0][index][-1]) for i in range(data_len)][::-1],
                [round(100 * result_lists[1][index][i] / result_lists[0][index][-1]) for i in range(data_len)][::-1],
            )
        else:
            y_list = (
                [round(100 * len(result_lists[0][index][i]) / len(result_lists[0][index][-1])) for i in range(data_len)][::-1],
                [round(100 * len(result_lists[1][index][i]) / len(result_lists[0][index][-1])) for i in range(data_len)][::-1],
            )
        full_coverage = result_lists[0][index][-1] if isinstance(result_lists[0][index][-1], int) else len(result_lists[0][index][-1])
        plot_result_list([list(range(data_len))] * 2, '2-Sided Relations Threshold', y_list, ylabel, msg +
                         f' Coverage, {legend}={bases[0]}, {bases[1]}\nFull Coverage={full_coverage}'
                         , max_threshold, True, legends=tuple(f'{legend}={base}' for base in bases))

