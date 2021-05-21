import pickle
import matplotlib.pyplot as plt


def plot_result_list(initial_x, xlabel, initial_y, ylabel, msg, max_threshold, is_min_2_sided):
    x = initial_x
    y = initial_y
    temp_dict = dict()
    for i in range(len(y)):
        temp_dict[y[i]] = (x[i], i)
    y = tuple(temp_dict.keys())
    x, i_list = zip(*temp_dict.values())
    plt.scatter(x, y)
    plt.grid()
    for xi, yi, ii in zip(x, y, i_list):
        label = f"{100 - ii}%" if not is_min_2_sided else f"{ii}"
        plt.annotate(label,
                     (xi, yi),
                     textcoords="offset points",
                     xytext=(0, 5),
                     ha='center',
                     )
    plt.suptitle(msg)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    remove_index = msg.find('\nFull Coverage')
    directory = msg[msg.find(', ') + 2:msg.find('\n')]
    msg = msg.replace(', ', '/')
    msg = msg.replace('\n', ',')
    plt.savefig(f"./../../Example Files/Plots/Confidence vs. Coverage/{directory}/{msg[:remove_index]} "
                f"{xlabel[:xlabel.find(' [%]')]}, max_threshold={max_threshold - 1}.png", dpi=400, bbox_inches='tight')
    plt.close()


def create_y_and_plot(initial_x, xlabel, msg, max_threshold, is_min_2_sided=False, ylabel='Agreements Ratio [%]\n(# of 2-Sided ToRs Agreements/# of 2-Sided ToRs)'):
    global result_list
    data_length = len(result_list[1])
    y = [round(100 * result_list[2][i]/result_list[1][i]) for i in range(min(data_length, max_threshold))]
    plot_result_list(initial_x, xlabel, y, ylabel, msg, max_threshold, is_min_2_sided)


for msg in ('I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary'):
    result_list0 = list()
    result_list5 = list()
    for mistake_threshold in range(101):
        with open(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold is {mistake_threshold}%.pickle', 'rb') as p:
            temp = pickle.load(p)
            result_list0 += [temp[0]]
            result_list5 += [temp[1]]
    assert result_list0 != list()
    assert result_list5 != list()
    for result_list, base in ((result_list0, 0), (result_list5, 5)):
        result_list = list(zip(*result_list))
        data_len = len(result_list[0])
        for max_threshold in (41, 101):
            x = [round(100 * result_list[0][i] / result_list[0][-1]) for i in range(data_len)]
            create_y_and_plot(x[:max_threshold], 'Overall Coverage [%]\n(# of ToRs/Original # of ToRs)', msg +
                             f', Base 2-Sided Threshold={base}\nFull Coverage={result_list[0][-1]}', max_threshold)
            x = [round(100 * result_list[1][i] / result_list[1][-1]) for i in range(data_len)]
            create_y_and_plot(x[:max_threshold], '2-Sided Coverage [%]', msg +
                             f', Base 2-Sided Threshold={base}\nFull Coverage={result_list[1][-1]}', max_threshold)
            x = [round(100 * len(result_list[3][i]) / len(result_list[3][-1])) for i in range(data_len)]
            create_y_and_plot(x[:max_threshold], 'AS Coverage [%]', msg +
                             f', Base 2-Sided Threshold={base}\nFull Coverage={len(result_list[3][-1])}', max_threshold)
            x = [round(100 * len(result_list[4][i]) / len(result_list[4][-1])) for i in range(data_len)]
            create_y_and_plot(x[:max_threshold], 'AS Coverage (2-Sided Perspective) [%]', msg +
                             f', Base 2-Sided Threshold={base}\nFull Coverage={len(result_list[4][-1])}', max_threshold)


for msg in ('I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary'):
    result_list0 = list()
    result_list90 = list()
    for min_2_sided in range(31):
        with open(f'./../../Pickles/2-Sides Requirement/{msg}/Requirement of at least '
                  f'{min_2_sided} 2-Sided ToRs.pickle', 'rb') as p:
            temp = pickle.load(p)
            result_list0 += [temp[0]]
            result_list90 += [temp[1]]
    assert result_list0 != list()
    assert result_list90 != list()

    for result_list, base in ((result_list0, 0), (result_list90, 90)):
        result_list = list(zip(*result_list))
        data_len = len(result_list[0])
        x = [round(100 * result_list[0][i] / result_list[0][0]) for i in range(data_len)]
        create_y_and_plot(x, 'Overall Coverage [%]\n(# of ToRs/Original # of ToRs)', msg +
                         f', Base Agreements Ratio Threshold={base}\nFull Coverage={result_list[0][0]}', data_len, True)
        x = [round(100 * result_list[1][i] / result_list[1][0]) for i in range(data_len)]
        create_y_and_plot(x, '2-Sided Coverage [%]', msg + f', Base Agreements Ratio Threshold={base}\n'
                                                          f'Full Coverage={result_list[1][0]}', data_len, True)
        x = [round(100 * len(result_list[3][i]) / len(result_list[3][0])) for i in range(data_len)]
        create_y_and_plot(x, 'AS Coverage [%]', msg + f', Base Agreements Ratio Threshold={base}\n'
                                                     f'Full Coverage={len(result_list[3][0])}', data_len, True)
        x = [round(100 * len(result_list[4][i]) / len(result_list[4][0])) for i in range(data_len)]
        create_y_and_plot(x, 'AS Coverage (2-Sided Perspective) [%]', msg + f', Base Agreements'
                                                                            f' Ratio Threshold={base}\n'
                                                                            f'Full Coverage='
                                                                            f'{len(result_list[4][0])}', data_len, True)





