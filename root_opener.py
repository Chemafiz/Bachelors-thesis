import matplotlib.pyplot as plt
import numpy as np
import uproot
import os
# import seaborn as sns


def build_hist(trees, features_names, baseline_tree, best_threshold_tree, outliers_cut_off):
    len_feature = len(features_names)
    fig, axes = plt.subplots(nrows=4 * len_feature, ncols=1, figsize=(10, len_feature * 20))

    current_axis = 0
    for feature in features_names:
        print(feature)
        #histogram wszystkich
        ax = axes[current_axis]

        x_min, x_max = None, None
        if feature in outliers_cut_off:
            x_min, x_max = outliers_cut_off[feature]

        baseline_data = np.array(baseline_tree[feature].array())
        optimal_threshold_data = np.array(best_threshold_tree[feature].array())

        if x_min or x_max:
            baseline_data = cut_outliers(baseline_data, x_min, x_max)
            optimal_threshold_data = cut_outliers(optimal_threshold_data, x_min, x_max)

        baseline_histogram = ax.hist(baseline_data, bins=50, label="Baseline", alpha=0.7)
        optimal_threshold_histogram = ax.hist(optimal_threshold_data, bins=50, label="Best threshold", alpha=0.7)

        for path, tree in trees.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10 + int(path.split(".")[-3][-1])
            hist_params = tree[feature].array()
            data = np.array(hist_params)

            if x_min or x_max:
                data = cut_outliers(data, x_min, x_max)

            y, binEdges = np.histogram(data, bins=50)
            bincenters = 0.5 * (binEdges[1:] + binEdges[:-1])
            ax.plot(bincenters, y, label=f"threshold = {threshold_value}")


        if x_min or x_max:
            ax.set_xlim(x_min, x_max)

        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Linear histogram for {feature}", fontweight='bold')
        ax.legend()


        #histogram tylko dwa
        current_axis += 1
        ax = axes[current_axis]

        baseline_histogram = ax.hist(baseline_data, bins=50, label="Baseline", alpha=0.7)
        optimal_threshold_histogram = ax.hist(optimal_threshold_data, bins=50, label="Best threshold", alpha=0.7)

        for path, tree in trees.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10 + int(path.split(".")[-3][-1])
            hist_params = tree[feature].array()
            data = np.array(hist_params)

            if x_min or x_max:
                data = cut_outliers(data, x_min, x_max)

            y, binEdges = np.histogram(data, bins=50)
            bincenters = 0.5 * (binEdges[1:] + binEdges[:-1])
            ax.plot(bincenters, y, label=f"threshold = {threshold_value}")

        if x_min or x_max:
            ax.set_xlim(x_min, x_max)
        ax.set_yscale("log")
        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Logarithmic histogram for {feature}", fontweight='bold')
        ax.legend()

        #ghosts factor
        current_axis += 1
        ax = axes[current_axis]
        for path, tree in trees.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10 + int(path.split(".")[-3][-1])
            hist_params = tree["isMatched"].array()
            data = np.array(hist_params)
            ratio = np.count_nonzero(data == 0) / data.shape[0] * 100
            ax.scatter(threshold_value, ratio, c="black")

        baseline_ghosts = np.array(baseline_tree["isMatched"].array())
        baseline_ghost_ratio = np.count_nonzero(baseline_ghosts == 0) / baseline_ghosts.shape[0] * 100
        optimal_threshold_ghosts = np.array(best_threshold_tree["isMatched"].array())
        optimal_threshold_ghost_ratio = np.count_nonzero(optimal_threshold_ghosts == 0) / optimal_threshold_ghosts.shape[0] * 100

        ax.scatter(0, baseline_ghost_ratio, label="baseline ghost ratio")
        ax.scatter(0.45, optimal_threshold_ghost_ratio, label="optimal threshold ghost ratio")

        ax.set_xlabel("threshold")
        ax.set_ylabel("[%]")
        ax.set_title(f"Ghosts", fontweight='bold')
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
        # print((h1[0] - h2[0])/(h1[0] + 1e-10))

        diff = 1 - optimal_threshold_histogram[0]/baseline_histogram[0]
        # ax.bar(baseline_histogram[1][:-1], diff, width=np.diff(baseline_histogram[1]), align="edge", label="Baseline - Optimal Threshold", alpha=1)
        ax.scatter(baseline_histogram[1][:-1], diff, label="Baseline - Optimal Threshold", alpha=1)

        if x_min or x_max:
            ax.set_xlim(x_min, x_max)
        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Residual histogram for {feature}", fontweight='bold')
        ax.legend()

        current_axis += 1


    # Dodaj legendę dla obu subwykresów
    plt.suptitle("Moore Classifier Benchmarks", fontsize=20, fontweight='bold', y=0.98-len_feature/100)

    # Zapisz wykres do pliku PDF
    plt.savefig("output_plot.pdf", format="pdf", bbox_inches="tight")
    print("Done!")


def cut_outliers(arr, x_min, x_max):
    return arr[(arr >= x_min) & (arr <= x_max)]



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


    features_to_analyse = ["p", "nFTHits", "chi2", "ndof", "ovtx_x", "ovtx_y", "pt", "phi","eta"]
    # p,nFTHits,chi2,ndof,ovtx_x,ovtx_y,pt,phi,eta, and isMatched for the ghost flag.
    outliers_cut_off = {"p": [0, 200_000], "pt": [0, 7000], "eta": [1, 7]}
    build_hist(trees, features_to_analyse, baseline, trees["Dumper_recTracks_0.3.root"], outliers_cut_off)





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