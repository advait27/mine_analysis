import matplotlib
matplotlib.use('TkAgg') # Use Tkinter-compatible backend
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve, label
from board import Board
import time

def _find_clusters(board_solution):
    """
    Helper function to find mine clusters.
    A cluster is any group of mines touching horizontally,
    vertically, or diagonally.
    """
    mine_map = (board_solution == -9).astype(int)
    structure = np.ones((3, 3), dtype=int)
    labeled_array, num_features = label(mine_map, structure=structure)
    return num_features

def _find_largest_opening(board_solution):
    """
    Helper function to find the size of the largest "opening".
    An opening is a connected component of '0' cells.
    """
    open_map = (board_solution == 0).astype(int)
    structure = np.ones((3, 3), dtype=int)
    labeled_array, num_features = label(open_map, structure=structure)
    
    if num_features == 0:
        return 0  # No '0' cells on the board
    
    component_sizes = np.bincount(labeled_array.ravel())[1:]
    return np.max(component_sizes)

def _count_edge_mines(board_solution):
    """Counts mines on the 0-indexed border."""
    h, w = board_solution.shape
    edge_mines = 0
    
    edge_mines += np.sum(board_solution[0, :] == -9)
    edge_mines += np.sum(board_solution[h-1, :] == -9)
    edge_mines += np.sum(board_solution[1:h-1, 0] == -9)
    edge_mines += np.sum(board_solution[1:h-1, w-1] == -9)
    
    return edge_mines

def _count_edge_zeros(board_solution):
    """Counts '0' cells on the 0-indexed border."""
    h, w = board_solution.shape
    edge_zeros = 0
    
    edge_zeros += np.sum(board_solution[0, :] == 0)
    edge_zeros += np.sum(board_solution[h-1, :] == 0)
    edge_zeros += np.sum(board_solution[1:h-1, 0] == 0)
    edge_zeros += np.sum(board_solution[1:h-1, w-1] == 0)
    
    return edge_zeros

def generate_analytics_data(height, width, num_mines, n_boards):
    """
    Generates a large number of boards and collects statistics.
    """
    print(f"Analytics: Generating {n_boards} boards... This may take a moment.")
    
    # --- Initialize data collectors ---
    white_cell_counts = []
    number_counts = np.zeros(9, dtype=int)
    cluster_counts = []
    neighborhood_sum = np.zeros((height, width), dtype=float)
    largest_opening_sizes = []
    edge_mine_counts = []
    edge_zero_counts = []
    
    kernel = np.ones((3, 3), dtype=int)
    
    # --- Simulation Loop ---
    start_time = time.time()
    for i in range(n_boards):
        b = Board(height, width, num_mines)
        solution = b.board
        
        # --- Collect Data ---
        white_cell_counts.append(np.sum(solution == 0))
        for j in range(9):
            number_counts[j] += np.sum(solution == j)
        cluster_counts.append(_find_clusters(solution))
        
        mine_map = (solution == -9).astype(int)
        neighborhood_map = convolve(mine_map, kernel, mode='constant', cval=0)
        neighborhood_sum += neighborhood_map
        
        largest_opening_sizes.append(_find_largest_opening(solution))
        edge_mine_counts.append(_count_edge_mines(solution))
        edge_zero_counts.append(_count_edge_zeros(solution))

    end_time = time.time()
    print(f"Data generation finished in {end_time - start_time:.2f} seconds.")

    neighborhood_avg = neighborhood_sum / n_boards
    
    return (white_cell_counts, number_counts, cluster_counts, 
            neighborhood_avg, largest_opening_sizes, 
            edge_mine_counts, edge_zero_counts)

def plot_analytics(height, width, num_mines, n_boards=1000):
    """
    Main function to run the full analytics suite and display all 8 plots.
    """
    try:
        data = generate_analytics_data(height, width, num_mines, n_boards)
    except Exception as e:
        print(f"Error during data generation: {e}")
        return
        
    (white_cell_counts, number_counts, cluster_counts, 
     neighborhood_avg, largest_opening_sizes, 
     edge_mine_counts, edge_zero_counts) = data
    
    # Create the 4x2 plot grid
    fig, axs = plt.subplots(4, 2, figsize=(15, 20)) # Width, Height
    fig.suptitle(f"Analytics for {n_boards} {height}x{width} Boards with {num_mines} Mines", 
                 fontsize=18) # Removed y=0.99, will control with subplots_adjust

    # --- Plot 1: Histogram of White Cells ---
    axs[0, 0].hist(white_cell_counts, bins=20, edgecolor='black', alpha=0.7)
    axs[0, 0].set_title('Histogram of "White Cells" (0s) per Board')
    axs[0, 0].set_xlabel('Number of "0" Cells')
    axs[0, 0].set_ylabel('Frequency (Boards)')
    
    # --- Plot 2: Distribution of Cell Numbers ---
    cell_numbers = [str(i) for i in range(9)]
    axs[0, 1].bar(cell_numbers, number_counts, color='skyblue', edgecolor='black')
    axs[0, 1].set_title('Total Distribution of Cell Numbers (All Boards)')
    axs[0, 1].set_xlabel('Cell Number')
    axs[0, 1].set_ylabel('Total Count')
    axs[0, 1].set_yscale('log')
    
    # --- Plot 3: Distribution of Mine Clusters ---
    if cluster_counts:
        bins = np.arange(min(cluster_counts), max(cluster_counts) + 2) - 0.5
    else:
        bins = 10
    axs[1, 0].hist(cluster_counts, bins=bins, edgecolor='black', alpha=0.7, color='green')
    axs[1, 0].set_title('Histogram of Mine Clusters per Board')
    axs[1, 0].set_xlabel('Number of Clusters')
    axs[1, 0].set_ylabel('Frequency (Boards)')
    if cluster_counts:
        axs[1, 0].set_xticks(np.unique(cluster_counts))
    
    # --- Plot 4: Mine Neighbourhood Heatmap ---
    im = axs[1, 1].imshow(neighborhood_avg, cmap='Reds', origin='upper')
    axs[1, 1].set_title('Average Mine Neighbours Heatmap')
    axs[1, 1].set_xlabel('Column')
    axs[1, 1].set_ylabel('Row')
    fig.colorbar(im, ax=axs[1, 1], label='Avg Mines in 3x3 Neighbourhood', fraction=0.046, pad=0.04)
    
    # --- Plot 5: Histogram of Largest Opening Size ---
    axs[2, 0].hist(largest_opening_sizes, bins=20, edgecolor='black', alpha=0.7, color='purple')
    axs[2, 0].set_title('Histogram of Largest "Opening" (0s-Cluster) Size')
    axs[2, 0].set_xlabel('Size of Largest "0" Cluster')
    axs[2, 0].set_ylabel('Frequency (Boards)')
    
    # --- Plot 6: Scatter Plot (White Cells vs. Clusters) ---
    axs[2, 1].scatter(white_cell_counts, cluster_counts, alpha=0.3)
    axs[2, 1].set_title('"White Cells" vs. Mine Clusters (per Board)')
    axs[2, 1].set_xlabel('Number of "White Cells" (0s)')
    axs[2, 1].set_ylabel('Number of Mine Clusters')
    
    # --- Plot 7: Histogram of Edge Mines ---
    if edge_mine_counts:
        bins = np.arange(min(edge_mine_counts), max(edge_mine_counts) + 2) - 0.5
    else:
        bins = 10
    axs[3, 0].hist(edge_mine_counts, bins=bins, edgecolor='black', alpha=0.7, color='orange')
    axs[3, 0].set_title('Histogram of Edge Mines per Board')
    axs[3, 0].set_xlabel('Number of Mines on Border')
    axs[3, 0].set_ylabel('Frequency (Boards)')
    if edge_mine_counts:
        axs[3, 0].set_xticks(np.unique(edge_mine_counts))
        
    # --- Plot 8: Histogram of Edge Zeros ---
    if edge_zero_counts:
        bins = np.arange(min(edge_zero_counts), max(edge_zero_counts) + 2) - 0.5
    else:
        bins = 10
    axs[3, 1].hist(edge_zero_counts, bins=bins, edgecolor='black', alpha=0.7, color='cyan')
    axs[3, 1].set_title('Histogram of Edge "Openings" (0s) per Board')
    axs[3, 1].set_xlabel('Number of "0" Cells on Border')
    axs[3, 1].set_ylabel('Frequency (Boards)')
    
    # --- *** FORMATTING FIX *** ---
    # Replace tight_layout with subplots_adjust
    # This gives manual control over spacing to prevent overlap.
    plt.subplots_adjust(
        left=0.1,    # Left margin
        right=0.9,   # Right margin
        top=0.95,    # Top margin (leaving space for suptitle)
        bottom=0.05, # Bottom margin
        wspace=0.3,  # Horizontal space between plots
        hspace=0.5   # Vertical space between plots
    )
    # --- *** END OF FIX *** ---
    
    plt.show()

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    print("Testing Analytics Module (8 Plots)...")
    plot_analytics(height=9, width=9, num_mines=10, n_boards=500)