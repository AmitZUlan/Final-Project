import multiprocessing as mp
import SourcesRenaming
import AnalyzeFiles, Sets, Swap
import PreliminaryClassifications
import SecondaryClassificationsPartA, SecondaryClassificationsPartB
import SecondaryClassificationsAnalysis, SuccessRate
import MistakesAnalysis
import FilterHeuristics
import ConfidenceCalculations


def start_processes(*functions):
    processes = []
    for function in functions:
        p = mp.Process(target=function)
        processes.append(p)
    for process in processes:
        process.start()
    for process in processes:
        process.join()


if __name__ == '__main__':
    # start_processes(SourcesRenaming.main())
    # start_processes(AnalyzeFiles.main(), Sets.main())
    # start_processes(Swap.main())
    # start_processes(PreliminaryClassifications.main(), SecondaryClassificationsPartA.main(), SecondaryClassificationsPartB.main())
    # start_processes(SecondaryClassificationsAnalysis.main(), SuccessRate.main())
    # start_processes(MistakesAnalysis.main())
    # start_processes(FilterHeuristics.main())
    # start_processes(ConfidenceCalculations.main())
    start_processes(SuccessRate.main2())


