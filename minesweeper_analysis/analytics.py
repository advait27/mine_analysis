import matplotlib

matplotlib.use("TkAgg")  # Use Tkinter-compatible backend

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve, label
from board import Board
import time


def _find_clusters(board_solution):
    """Find mine clusters (groups of touching mines)."""
    mine_map = (board_solution == -9).astype(int)
    structure = np.ones((3, 3), dtype=int)
    labeled, num_features = label(mine_map, structure=structure)
    return num_features


def _find_largest_opening(board_solution):
    """Find size of largest zero-cell opening."""
    open_map = (board_solution == 0).astype(int)
    structure = np.ones((3, 3), dtype=int)
    labeled, num_features = label(open_map, structure=structure)

    if num_features == 0:
        return 0

    component_sizes = np.bincount(labeled.ravel())[1:]
    return np.max(component_sizes)


def generate_analytics_data(height, width, num_mines, n_boards):
    """Generate simulated boards + collect stats."""
    print(f"Analytics: Generating {n_boards} boards...")

    white_cell_counts = []
    number_counts = np.zeros(9, dtype=int)
    cluster_counts = []
    neighborhood_sum = np.zeros((height, width), dtype=float)
    largest_opening_sizes = []

    kernel = np.ones((3, 3), dtype=int)

    start_time = time.time()

    for _ in range(n_boards):
        board = Board(height, width, num_mines)
        solution = board.board

        white_cell_counts.append(np.sum(solution == 0))

        for j in range(9):
            number_counts[j] += np.sum(solution == j)

        cluster_counts.append(_find_clusters(solution))
        largest_opening_sizes.append(_find_largest_opening(solution))

        # Mine neighbourhood heatmap
        mine_map = (solution == -9).astype(int)
        neighborhood_map = convolve(mine_map, kernel, mode="constant", cval=0)
        neighborhood_sum += neighborhood_map

    neighborhood_avg = neighborhood_sum / n_boards

    end_time = time.time()
    print(f"Finished in {end_time - start_time:.2f} seconds.")

    return (
        white_cell_counts,
        number_counts,
        cluster_counts,
        neighborhood_avg,
        largest_opening_sizes,
    )


def plot_analytics(height, width, num_mines, n_boards=1000):
    """Run analytics and show 6-plot 3×2 grid."""
    try:
        (
            white_cell_counts,
            number_counts,
            cluster_counts,
            neighborhood_avg,
            largest_opening_sizes,
        ) = generate_analytics_data(height, width, num_mines, n_boards)
    except Exception as e:
        print(f"Error: {e}")
        return

    # -----------------------
    # 3 × 2 grid figure
    # -----------------------
    fig, axs = plt.subplots(3, 2, figsize=(15, 15))
    fig.suptitle(
        f"Analytics for {n_boards} boards of {height}×{width} with {num_mines} mines",
        fontsize=18,
    )

    # -----------------------
    # Plot 1 — Histogram of zeros
    # -----------------------
    axs[0, 0].hist(white_cell_counts, bins=20, edgecolor="black", alpha=0.7)
    axs[0, 0].set_title('Histogram of "White Cells" (0s)')
    axs[0, 0].set_xlabel("Number of 0-cells")
    axs[0, 0].set_ylabel("Frequency")

    # -----------------------
    # Plot 2 — Distribution of numbers
    # -----------------------
    labels = [str(i) for i in range(9)]
    axs[0, 1].bar(labels, number_counts, color="skyblue", edgecolor="black")
    axs[0, 1].set_title("Distribution of Cell Numbers (0–8)")
    axs[0, 1].set_xlabel("Cell Value")
    axs[0, 1].set_ylabel("Total Count")
    axs[0, 1].set_yscale("log")

    # -----------------------
    # Plot 3 — Mine clusters
    # -----------------------
    bins = (
        np.arange(min(cluster_counts), max(cluster_counts) + 2) - 0.5
        if cluster_counts
        else 10
    )
    axs[1, 0].hist(
        cluster_counts, bins=bins, edgecolor="black", alpha=0.7, color="green"
    )
    axs[1, 0].set_title("Mine Cluster Count")
    axs[1, 0].set_xlabel("Clusters per Board")
    axs[1, 0].set_ylabel("Frequency")

    # -----------------------
    # Plot 4 — Neighbourhood heatmap
    # -----------------------
    im = axs[1, 1].imshow(neighborhood_avg, cmap="Reds", origin="upper")
    axs[1, 1].set_title("Average Mines in 3×3 Neighbourhood")
    axs[1, 1].set_xlabel("Column")
    axs[1, 1].set_ylabel("Row")
    fig.colorbar(im, ax=axs[1, 1], fraction=0.046, pad=0.04)

    # -----------------------
    # Plot 5 — Largest openings
    # -----------------------
    axs[2, 0].hist(
        largest_opening_sizes, bins=20, edgecolor="black", alpha=0.7, color="purple"
    )
    axs[2, 0].set_title('Size of Largest 0-Cluster ("Opening")')
    axs[2, 0].set_xlabel("Cluster Size")
    axs[2, 0].set_ylabel("Frequency")

    # -----------------------
    # Plot 6 — Scatter: White cells vs. clusters
    # -----------------------
    axs[2, 1].scatter(white_cell_counts, cluster_counts, alpha=0.3)
    axs[2, 1].set_title("0-Cells vs. Mine Clusters")
    axs[2, 1].set_xlabel("White Cells")
    axs[2, 1].set_ylabel("Mine Clusters")

    # -------- Layout spacing --------
    plt.subplots_adjust(
        left=0.08,
        right=0.95,
        top=0.93,
        bottom=0.07,
        wspace=0.25,
        hspace=0.40,
    )

    plt.show()


# For manual testing
if __name__ == "__main__":
    plot_analytics(9, 9, 10, 300)
