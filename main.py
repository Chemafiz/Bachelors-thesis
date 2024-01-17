import matplotlib.pyplot as plt
import numpy as np
import uproot
import os



def build_hist(features, threshold_scan_roots, baseline_root, best_threshold_root, bins=50):
    len_feature = len(features)
    fig, axes = plt.subplots(nrows=3 * len_feature, ncols=1, figsize=(10, len_feature * 20))

    current_axis = 0
    for feature, feature_attributes in features.items():
        # dane baseline i klasyfikatora
        baseline_data = np.array(baseline_root[feature].array())
        optimal_threshold_data = np.array(best_threshold_root[feature].array())

        # odczytywanie parametrów odcięcia wartości odstających
        x_min, x_max = None, None
        if feature_attributes[2]:
            x_min, x_max = feature_attributes[2]

        # odrzucanie wartości spoza przedziału
        if x_min or x_max:
            baseline_data = cut_outliers(baseline_data, x_min, x_max)
            optimal_threshold_data = cut_outliers(optimal_threshold_data, x_min, x_max)


        ax = axes[current_axis]
        # rysowanie histogramów
        ax.hist(baseline_data, bins=bins, label="Baseline", alpha=1)
        ax.hist(optimal_threshold_data, bins=bins, label="Optimal threshold", alpha=1)

        # rysowanie histogramów pozostałych klasyfikatorów
        for path, tree in threshold_scan_roots.items():
            # parsowanie ścieżki pliku w celu odczytania wartości thresholdu
            threshold_value = int(path.split(".")[-2][-1]) / 10 + int(path.split(".")[-3][-1])
            hist_params = tree[feature].array()
            data = np.array(hist_params)

            if x_min or x_max:
                data = cut_outliers(data, x_min, x_max)

            ax.hist(data, bins=bins, label=f"threshold = {threshold_value}", alpha=0.7)


        if x_min or x_max:
            ax.set_xlim(x_min, x_max)

        ax.set_xlabel(f"{feature} {feature_attributes[1]}")
        ax.set_title(f"Linear histogram for '{feature_attributes[0]}'", fontweight='bold')
        ax.legend()


        #histogram tylko dwa
        current_axis += 1
        ax = axes[current_axis]

        baseline_histogram = ax.hist(baseline_data, bins=bins, label="Baseline", alpha=1)
        optimal_threshold_histogram = ax.hist(optimal_threshold_data, bins=bins, label="Optimal threshold", alpha=1)

        for path, tree in threshold_scan_roots.items():
            threshold_value = int(path.split(".")[-2][-1]) / 10 + int(path.split(".")[-3][-1])
            hist_params = tree[feature].array()
            data = np.array(hist_params)

            if x_min or x_max:
                data = cut_outliers(data, x_min, x_max)

            ax.hist(data, bins=bins, label=f"threshold = {threshold_value}", alpha=1)


        if x_min or x_max:
            ax.set_xlim(x_min, x_max)
        ax.set_yscale("log")
        ax.set_xlabel(f"{feature} {feature_attributes[1]}")
        ax.set_title(f"Logarithmic histogram for '{feature_attributes[0]}'", fontweight='bold')
        ax.legend()



        #residuals
        current_axis += 1
        ax = axes[current_axis]

        # charakterystyka histogramów
        optimal_threshold_points = optimal_threshold_histogram[0]
        baseline_points = baseline_histogram[0]

        # odrzucanie przedziałów gdzie ilość pomiarów mniejsza od 5
        mask = np.logical_or(optimal_threshold_points < 5.0, baseline_points < 5.0)
        optimal_threshold_points[mask] = np.nan
        baseline_points[mask] = np.nan

        # różnica względna pomiędzy histogramami (residuum)
        diff = 1 - optimal_threshold_points / baseline_points
        ax.scatter(baseline_histogram[1][:-1], diff, alpha=1, c="black", s=10)

        if x_min or x_max:
            ax.set_xlim(x_min, x_max)

        ax.set_ylim(-1, 1)
        ax.set_ylabel("(Baseline - OptimalThreshold) / Baseline")
        ax.set_xlabel(f"{feature} {feature_attributes[1]}")
        ax.set_title(f"Residual ratio for '{feature_attributes[0]}'", fontweight='bold')


        current_axis += 1


    # Dodaj legendę dla obu subwykresów
    plt.suptitle("Classifier model Benchmarks", fontsize=20, fontweight='bold', y=0.89)

    # Zapisz wykres do pliku PDF
    plt.savefig("analysis_file.pdf", format="pdf", bbox_inches="tight")
    print("Done!")


def cut_outliers(arr, x_min, x_max):
    return arr[(arr >= x_min) & (arr <= x_max)]



def load_files(path):
    output_hist_trees = {}
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)
        root_file = uproot.open(file_path)
        tree = root_file["Hits_detectors/"]
        output_hist_trees[file] = tree

    return output_hist_trees


if __name__ == "__main__":
    # parsowanie danych z pliku root
    threshold_scan_roots = load_files("data/threshold_scan_files")

    baseline_root = uproot.open("data/main_files/Dumper_recTracks_baseline.root")
    baseline_root = baseline_root["Hits_detectors/"]

    optimal_threshold_root = uproot.open("data/main_files/Dumper_recTracks_0.07.root")
    optimal_threshold_root = optimal_threshold_root["Hits_detectors/"]

    # ustawianie parametrów tworzonych wykresów
    features_to_analyse = {
        #zmienna: [tytuł wykresu, jednostka osi X, punkt odcięcia wartości odstających (min, max)]
        "p": ["Momentum", "[MeV/c]", (0, 70_000)],
        "pt": ["Transverse Momentum", "[MeV/c]", (0, 4000)],
        "ovtx_x": ["Position x", "[mm]", (-650, 650)],
        "ovtx_y": ["Position y", "[mm]", (-600, 600)],
        "phi": ["Azimuthal Angle", "[rad]", (-3.14, 3.14)],
        "eta": ["Pseudo rapidity", "", (1.75, 7)]}


    # tworzenie i zapis do pliku wykresów
    build_hist(features_to_analyse, threshold_scan_roots, baseline_root, optimal_threshold_root, bins=100)

