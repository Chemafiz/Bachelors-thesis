import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np
import uproot
# import pandas as pd
import os
import re


def build_hist(trees, features_names, baseline_tree, best_threshold_tree):
    fig, axes = plt.subplots(nrows=3 * len(features_names), ncols=1, figsize=(10, 40))

    current_axis = 0
    for feature in features_names:
        ax = axes[current_axis]
        # plt.figtext(0.4, 0.89, feature, fontsize=20)
        for path, tree in trees.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10
            hist_params = tree[feature].to_numpy()
            y = hist_params[0]
            x = hist_params[1]
            ax.bar(x[:-1], y, width=np.diff(x), align="edge", label=f"threshold = {threshold_value}", alpha=1.0)

        hist_params = baseline_tree[feature].to_numpy()
        y = hist_params[0]
        x = hist_params[1]
        ax.bar(x[:-1], y, width=np.diff(x), align="edge", label="Baseline", alpha=1.0)

        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Linear histogram for {feature}")
        ax.legend()



        current_axis += 1

        ax = axes[current_axis]
        for path, tree in trees.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10
            hist_params = tree[feature].to_numpy()
            y = hist_params[0]
            x = hist_params[1]
            ax.bar(x[:-1], y, width=np.diff(x), align="edge", label=f"threshold = {threshold_value}", alpha=0.5)
        ax.set_yscale('log')
        ax.set_xlabel("X-axis Label")
        ax.set_title(f"Logarithmic Histogram {feature}")
        ax.legend()

        current_axis += 1

    # # accuracy plot
    # thresholds = []
    # efficiencies = []
    # temp_tuple = {"tracks": [], "ghosts": []}
    # for path, data in eff.items():
    #     parsed_data = re.search(r'Output_(\d+)', path)
    #     if parsed_data:
    #         x = float('0.' + parsed_data.group(1)[1:])
    #         thresholds.append(x)
    #     efficiency = data[1]/data[0] * 100
    #     efficiencies.append(efficiency)
    #
    #     temp_tuple["tracks"].append(data[0])
    #     temp_tuple["ghosts"].append(data[1])
    #
    #
    # axes[2].plot(thresholds, efficiencies, marker='o', linestyle='-')
    # axes[2].set_title("ghosts/tracks")
    # axes[2].set_xlabel("threshold")
    # axes[2].set_ylabel("efficiency [%]")



    # print(temp_tuple)
    # bottom = np.zeros(4)
    # for sex, sex_count in temp_tuple.items():
    #     p = axes[3].bar(thresholds, sex_count, 0.05, label=sex, bottom=bottom)
    #     bottom += np.array(sex_count)
    #
    #     axes[3].bar_label(p, label_type='center')
    # axes[3].legend()
    #
    # nowe_ticks = np.arange(0.0, 1, 0.1)
    # axes[3].set_xticks(nowe_ticks)


    # Dodaj legendę dla obu subwykresów
    plt.suptitle("Moore Classifier Benchmarks", fontsize=20, fontweight='bold', y=0.95)

    # Zapisz wykres do pliku PDF
    plt.savefig("output_plot.pdf", format="pdf", bbox_inches="tight")
    print("Done!")





def search_directory(folder_path, output_log_files):
    output_hist_trees = {}
    all_dir = os.listdir(folder_path)
    for output_dir in all_dir:
        dir_path = os.path.join(folder_path, output_dir)
        if os.path.isdir(dir_path):
            output_hist_file = os.path.join(dir_path, 'output_hist.root')
            output_log_file = os.path.join(dir_path, 'log.log')
            if os.path.exists(output_hist_file):
                root_file = uproot.open(output_hist_file)
                tree = root_file["Track/DownstreamTrackChecker/Downstream/"]
                output_hist_trees[output_hist_file] = tree
            if os.path.exists(output_log_file):
                with open(output_log_file, 'r') as log_file:
                    for line in log_file:
                        if 'DownstreamTrackChecker' in line and 'INFO **** Downstream' in line:
                            parsed_line = re.search(r'\b(\d+)\stracks including\s+(\d+)\sghosts', line)
                            if parsed_line:
                                tracks_number = int(parsed_line.group(1))
                                ghosts_number = int(parsed_line.group(2))
                                output_log_files[output_log_file] = (tracks_number, ghosts_number)
                                break
    return output_hist_trees


def load_files(path):
    output_hist_trees = {}
    files = os.listdir(path)

    for file in files:
        file_path = os.path.join(path, file)

        root_file = uproot.open(file_path)
        tree = root_file["Track/DownstreamTrackChecker/Downstream/"]
        output_hist_trees[file] = tree

    return output_hist_trees

if __name__ == "__main__":
    log_paths = {}
    trees = load_files("histograms")
    # trees = search_directory("histograms", log_paths)

    baseline_root_file = uproot.open("baseline_output_hist.root")
    baseline_tree = baseline_root_file["Track/DownstreamTrackChecker/Downstream/"]
    for key in baseline_tree.keys():
        print(key)
    # best_threshold_file = uproot.open("best_threshold_nhist.root")
    # best_threshold_tree = best_threshold_file["Track/DownstreamTrackChecker/Downstream/"]

    print(trees)
    build_hist(trees, ["nPV_Total", "nHits_all_Total"], baseline_tree, baseline_tree)

