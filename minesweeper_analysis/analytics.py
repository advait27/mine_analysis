import matplotlib
matplotlib.use('TkAgg') # <-- ADD THIS LINE
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
    
    Args:
        board_solution (np.ndarray): The solution board (with -9 for mines).

    Returns:
        int: The number of distinct mine clusters.
    """
    # Create a binary map: 1 for mine, 0 otherwise
    mine_map = (board_solution == -9).astype(int)
    
    # Define the "structure" for connectivity.
    # This 3x3 matrix of 1s means we check all 8 neighbors 
    # (horizontal, vertical, and diagonal).
    structure = np.ones((3, 3), dtype=int)
    
    # 'label' finds all "connected components"
    # 'num_features' will be the number of clusters
    labeled_array, num_features = label(mine_map, structure=structure)
    
    return num_features

def generate_analytics_data(height, width, num_mines, n_boards):
    """
    Generates a large number of boards and collects statistics.

    Args:
        height (int): Board height.
        width (int): Board width.
        num_mines (int): Number of mines.
        n_boards (int): Number of boards to simulate.

    Returns:
        tuple: A tuple containing all the collected data:
               (white_cell_counts, number_counts, cluster_counts, neighborhood_avg)
    """
    print(f"Analytics: Generating {n_boards} boards... This may take a moment.")
    
    # --- Initialize data collectors ---
    
    # 1. For "White Cell" (0s) histogram
    white_cell_counts = [] # List to store the count of '0's for each board
    
    # 2. For number distribution (0-8)
    number_counts = np.zeros(9, dtype=int) # Index 0 holds count of 0s, index 1 count of 1s...
    
    # 3. For mine cluster histogram
    cluster_counts = [] # List to store the number of clusters for each board
    
    # 4. For neighborhood heatmap
    # This 2D array will sum up all neighborhood maps
    neighborhood_sum = np.zeros((height, width), dtype=float)
    
    # --- Define the kernel for convolution (Plot 4) ---
    # This kernel will help us count mines in a 3x3 neighborhood
    kernel = np.ones((3, 3), dtype=int)
    
    # --- Simulation Loop ---
    start_time = time.time()
    for i in range(n_boards):
        # Create a new board
        b = Board(height, width, num_mines)
        solution = b.board
        
        # --- Collect Data ---
        
        # 1. White Cells: Count cells that are '0'
        white_cell_counts.append(np.sum(solution == 0))
        
        # 2. Number Distribution: Count cells 0 through 8
        for j in range(9):
            number_counts[j] += np.sum(solution == j)
            
        # 3. Mine Clusters: Find clusters
        cluster_counts.append(_find_clusters(solution))
        
        # 4. Neighborhood Heatmap
        # Create a binary (1=mine, 0=not)
        mine_map = (solution == -9).astype(int)
        # 'convolve' slides the 3x3 kernel over the mine_map
        # The result is a (height, width) grid where each cell
        # holds the count of mines in its 3x3 neighborhood.
        neighborhood_map = convolve(mine_map, kernel, mode='constant', cval=0)
        # Add this board's map to our total sum
        neighborhood_sum += neighborhood_map
        
    end_time = time.time()
    print(f"Data generation finished in {end_time - start_time:.2f} seconds.")

    # --- Finalize Data ---
    # 4. Average the neighborhood map
    neighborhood_avg = neighborhood_sum / n_boards
    
    return white_cell_counts, number_counts, cluster_counts, neighborhood_avg

def plot_analytics(height, width, num_mines, n_boards=1000):
    """
    Main function to run the full analytics suite and display the plots.
    """
    # 1. Generate all the data
    try:
        data = generate_analytics_data(height, width, num_mines, n_boards)
    except Exception as e:
        print(f"Error during data generation: {e}")
        return
        
    white_cell_counts, number_counts, cluster_counts, neighborhood_avg = data
    
    # 2. Create the 2x2 plot grid
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"Analytics for {n_boards} {height}x{width} Boards with {num_mines} Mines", fontsize=16)

    # --- Plot 1: Histogram of White Cells ---
    ax1 = axs[0, 0]
    ax1.hist(white_cell_counts, bins=20, edgecolor='black', alpha=0.7)
    ax1.set_title('Histogram of "White Cells" (0s) per Board')
    ax1.set_xlabel('Number of "0" Cells')
    ax1.set_ylabel('Frequency (Number of Boards)')
    
    # --- Plot 2: Distribution of Cell Numbers ---
    ax2 = axs[0, 1]
    cell_numbers = [str(i) for i in range(9)]
    ax2.bar(cell_numbers, number_counts, color='skyblue', edgecolor='black')
    ax2.set_title('Total Distribution of Cell Numbers (All Boards)')
    ax2.set_xlabel('Cell Number')
    ax2.set_ylabel('Total Count')
    ax2.set_yscale('log') # Use log scale as '0' and '1' will be far more common
    
    # --- Plot 3: Distribution of Mine Clusters ---
    ax3 = axs[1, 0]
    # Calculate bins for a clean integer histogram
    if cluster_counts:
        max_clusters = max(cluster_counts)
        bins = np.arange(min(cluster_counts), max_clusters + 2) - 0.5
    else:
        bins = 10
    ax3.hist(cluster_counts, bins=bins, edgecolor='black', alpha=0.7, color='green')
    ax3.set_title('Histogram of Mine Clusters per Board')
    ax3.set_xlabel('Number of Clusters')
    ax3.set_ylabel('Frequency (Number of Boards)')
    ax3.set_xticks(np.unique(cluster_counts)) # Show ticks for each cluster number
    
    # --- Plot 4: Mine Neighbourhood Heatmap ---
    ax4 = axs[1, 1]
    # 'imshow' creates the heatmap. 'origin="upper"' is standard.
    im = ax4.imshow(neighborhood_avg, cmap='Reds', origin='upper')
    ax4.set_title('Average Mine Neighbours Heatmap')
    ax4.set_xlabel('Column')
    ax4.set_ylabel('Row')
    # Add a color bar to show the scale
    fig.colorbar(im, ax=ax4, label='Average Mines in 3x3 Neighbourhood')
    
    # --- Show the plots ---
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to make room for suptitle
    plt.show()

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # This part only runs when you execute this file directly
    print("Testing Analytics Module...")
    # Run analytics for a small 5x5 board, 100 times (for a quick test)
    plot_analytics(height=5, width=5, num_mines=5, n_boards=100)
    
    # Run analytics for the Easy configuration
    plot_analytics(height=9, width=9, num_mines=10, n_boards=1000)