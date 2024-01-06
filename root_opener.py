import matplotlib.pyplot as plt
import numpy as np
import uproot
from scipy.stats import chisquare
import os
import re
import seaborn as sns


def build_hist(trees, features_names, baseline_tree, best_threshold_tree):
    len_feature = len(features_names)
    fig, axes = plt.subplots(nrows=3 * len_feature, ncols=1, figsize=(10, len_feature * 20))

    current_axis = 0
    for feature in features_names:
        print(feature)
        #histogram wszystkich
        ax = axes[current_axis]

        hist_params = np.array(baseline_tree[feature].array())
        h1 = ax.hist(hist_params, bins=50, label="Baseline", alpha=0.7)

        hist_params = np.array(best_threshold_tree[feature].array())
        h2 = ax.hist(hist_params, bins=50, label="Best threshold", alpha=0.7)

        for path, tree in trees.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10 + int(path.split(".")[-3][-1])
            hist_params = tree[feature].array()
            data = np.array(hist_params)

            # ax.hist(data, bins=50, label=f"threshold = {threshold_value}", alpha=0.5)
            # sns.kdeplot(data, label=f"threshold = {threshold_value}", ax=ax)

            y, binEdges = np.histogram(data, bins=50)
            bincenters = 0.5 * (binEdges[1:] + binEdges[:-1])
            ax.plot(bincenters, y, label=f"threshold = {threshold_value}")


        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Linear histogram for {feature}", fontweight='bold')
        ax.legend()


        #histogram tylko dwa
        current_axis += 1

        ax = axes[current_axis]

        hist_params = np.array(baseline_tree[feature].array())
        ax.hist(hist_params, bins=50, label="Baseline", alpha=0.7)

        hist_params = np.array(best_threshold_tree[feature].array())
        ax.hist(hist_params, bins=50, label="Best threshold", alpha=0.7)

        for path, tree in trees.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10 + int(path.split(".")[-3][-1])
            hist_params = tree[feature].array()
            data = np.array(hist_params)
            # ax.bar(x[:-1], y, width=np.diff(x), align="edge", label=f"threshold = {threshold_value}", alpha=0.5)
            # ax.plot(x[:-1], y, label=f"threshold = {threshold_value}", alpha=1)
            # ax.hist(data, bins=50, label=f"threshold = {threshold_value}", alpha=0.5)

            y, binEdges = np.histogram(data, bins=50)
            bincenters = 0.5 * (binEdges[1:] + binEdges[:-1])
            ax.plot(bincenters, y, label=f"threshold = {threshold_value}")




        ax.set_yscale("log")

        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Logarithmic histogram for {feature}", fontweight='bold')
        ax.legend()


        #residuale
        current_axis += 1
        ax = axes[current_axis]

        # hist_params_baseline = np.array(baseline_tree[feature].array())
        # hist_params_best_threshold = np.array(best_threshold_tree[feature].array())

        # h1 = plt.hist(hist_params_baseline, bins=50)
        # h2 = plt.hist(hist_params_best_threshold, bins=50)

        # bin_edges = np.arange(hist_params_baseline.min(), hist_params_baseline.max(), 50)
        # baseline_hist, _ = np.histogram(hist_params_baseline, bins=bin_edges)
        # best_threshold_hist, _ = np.histogram(hist_params_best_threshold, bins=bin_edges)

        # calculate the difference
        # diff = baseline_hist - best_threshold_hist

        ax.bar(h2[1][:-1], h1[0] - h2[0], width= np.diff(h2[1]), align="edge", label="Baseline - Optimal Threshold", alpha=1)
        # sns.barplot(x=bin_edges[:-1], y=diff, color='tab:blue', ec='k', width=1, alpha=0.8, ax=ax)
        # ax.bar(bin_edges[:-1], h_diff, align="edge", label="Best threshold - baseline", alpha=0.5)
        # # ax.plot(x_baseline[:-1], y_difference, label="Best threshold - baseline", alpha=0.5)

        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Residual histogram for {feature}", fontweight='bold')
        ax.legend()

        current_axis += 1


    # Dodaj legendę dla obu subwykresów
    plt.suptitle("Moore Classifier Benchmarks", fontsize=20, fontweight='bold', y=0.96-len_feature/100)

    # Zapisz wykres do pliku PDF
    plt.savefig("output_plot.pdf", format="pdf", bbox_inches="tight")
    print("Done!")





def load_files(path):
    output_hist_trees = {}
    files = os.listdir(path)

    for file in files:
        file_path = os.path.join(path, file)
        root_file = uproot.open(file_path)
        print(root_file)
        tree = root_file["Hits_detectors/"]
        output_hist_trees[file] = tree

    return output_hist_trees

if __name__ == "__main__":
    log_paths = {}
    trees = load_files("histograms")


###################################
    dumper = uproot.open("Dumper_tracks.root")
    dumper = dumper["Hits_detectors/"]
    for key in dumper.keys():
        print(key)

    baseline = uproot.open("Dumper_recTracks_baseline.root")
    baseline = baseline["Hits_detectors/"]
##################################################


    features_to_analyse = ["p", "chi2", "Velo_lhcbID", "phi", "px", "py", "pt",  ]
    #Momentum, Chi2PerDoF, nLHCbID, Phi, Position X, Position Y, Pt, Tx, Ty, Pseudo rapidity
    build_hist(trees, features_to_analyse, baseline, trees["Dumper_recTracks_0.3.root"])





# def search_directory(folder_path, output_log_files):
#     output_hist_trees = {}
#     all_dir = os.listdir(folder_path)
#     for output_dir in all_dir:
#         dir_path = os.path.join(folder_path, output_dir)
#         if os.path.isdir(dir_path):
#             output_hist_file = os.path.join(dir_path, 'output_hist.root')
#             output_log_file = os.path.join(dir_path, 'log.log')
#             if os.path.exists(output_hist_file):
#                 root_file = uproot.open(output_hist_file)
#                 tree = root_file["Track/DownstreamTrackChecker/Downstream/"]
#                 output_hist_trees[output_hist_file] = tree
#             if os.path.exists(output_log_file):
#                 with open(output_log_file, 'r') as log_file:
#                     for line in log_file:
#                         if 'DownstreamTrackChecker' in line and 'INFO **** Downstream' in line:
#                             parsed_line = re.search(r'\b(\d+)\stracks including\s+(\d+)\sghosts', line)
#                             if parsed_line:
#                                 tracks_number = int(parsed_line.group(1))
#                                 ghosts_number = int(parsed_line.group(2))
#                                 output_log_files[output_log_file] = (tracks_number, ghosts_number)
#                                 break
#     return output_hist_trees