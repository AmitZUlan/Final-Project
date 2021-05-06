import pickle
from os import path
import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np


for msg in ['I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary']:
    with open(f'./../../Pickles/{msg} Mistakes.pickle', 'rb') as p:
        mistakes = pickle.load(p)
    x = [i for i in range(100)]
    y = [list(mistakes.values()).count(xi) for xi in x]
    plt.plot(x, y)
    plt.grid()
    plt.yticks([int(max(y)/50) * i for i in range(50)])
    plt.xlabel('# of Mistakes')
    plt.ylabel('Count of ASNs with x Mistakes')
    plt.suptitle('Mistakes Histogram')
    plt.show()


for msg in ['I_E Dictionary', 'Remarks Dictionary', 'Sets Dictionary']:
    result_list = list()
    for mistake_threshold in range(1000):
        if not path.exists(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold {mistake_threshold}.pickle'): continue
        with open(f'./../../Pickles/Mistakes/{msg}/Mistake Threshold {mistake_threshold}.pickle', 'rb') as p:
            result_list += pickle.load(p)
    result_list = list(zip(*result_list))
    mistake_threshold = np.array(result_list[0])
    two_sided_classifications = np.array(result_list[1])
    two_sided_agreements = np.array(result_list[2])
    fig, plots = plt.subplots(5, sharex=True)
    plots[0].plot(mistake_threshold, two_sided_classifications)#, linewidths=0.1)
    plots[1].plot(mistake_threshold, two_sided_agreements)#, linewidths=0.1)
    plots[2].plot(mistake_threshold, two_sided_classifications - two_sided_agreements)#, linewidths=0.1)
    plots[3].plot(mistake_threshold, two_sided_classifications * two_sided_agreements)#, linewidths=0.1)
    plots[4].plot(mistake_threshold, two_sided_classifications * two_sided_agreements)#, linewidths=0.1)
    fig.suptitle(msg)
    plt.xticks([i for i in range(10, 200)])
    plt.xlabel('Mistake Threshold')
    plots[0].set_ylabel('2-Sided Classifications')
    plots[1].set_ylabel('2-Sided Agreements')
    plots[2].set_ylabel('2-Sided Disagreements')
    plots[3].set_ylabel('Multiply')
    plots[4].set_ylabel('Ratio')


    plt.show()

