import matplotlib
matplotlib.use('TkAgg') # Use Tkinter-compatible backend
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve, label
from board import Board
import time

# Imports for interactive plots
import plotly.express as px
import pandas as pd

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
    # Create a binary map: 1 for '0' cell, 0 otherwise
    open_map = (board_solution == 0).astype(int)
    
    # Define connectivity (8-way, just like for mines)
    structure = np.ones((3, 3), dtype=int)
    
    # Find all connected components of '0's
    labeled_array, num_features = label(open_map, structure=structure)
    
    if num_features == 0:
        return 0  # No '0' cells on the board
    
    # Get the size of each component
    # np.bincount counts occurrences of each label (0, 1, 2...)
    # We slice [1:] to ignore the background (label 0)
    component_sizes = np.bincount(labeled_array.ravel())[1:]
    
    # Return the size of the largest component
    return np.max(component_sizes)

def generate_analytics_data(height, width, num_mines, n_boards):
    """
    Generates a large number of boards and collects statistics.
    (MODIFIED to also collect largest opening size)
    """
    print(f"Analytics: Generating {n_boards} boards... This may take a moment.")
    
    # --- Initialize data collectors ---
    white_cell_counts = []
    number_counts = np.zeros(9, dtype=int)
    cluster_counts = []
    neighborhood_sum = np.zeros((height, width), dtype=float)
    
    # --- NEW: Add list for largest opening sizes ---
    largest_opening_sizes = [] 
    
    kernel = np.ones((3, 3), dtype=int)
    
    # --- Simulation Loop ---
    start_time = time.time()
    for i in range(n_boards):
        b = Board(height, width, num_mines)
        solution = b.board
        
        # --- Collect Data ---
        
        # 1. White Cells
        white_cell_counts.append(np.sum(solution == 0))
        
        # 2. Number Distribution
        for j in range(9):
            number_counts[j] += np.sum(solution == j)
            
        # 3. Mine Clusters
        cluster_counts.append(_find_clusters(solution))
        
        # 4. Neighborhood Heatmap
        mine_map = (solution == -9).astype(int)
        neighborhood_map = convolve(mine_map, kernel, mode='constant', cval=0)
        neighborhood_sum += neighborhood_map
        
        # --- NEW: Collect largest opening size ---
        largest_opening_sizes.append(_find_largest_opening(solution))
        
    end_time = time.time()
    print(f"Data generation finished in {end_time - start_time:.2f} seconds.")

    neighborhood_avg = neighborhood_sum / n_boards
    
    # --- MODIFIED: Return the new data ---
    return (white_cell_counts, number_counts, cluster_counts, 
            neighborhood_avg, largest_opening_sizes)

def plot_analytics(height, width, num_mines, n_boards=1000):
    """
    Main function to run the original 4 static plots.
    """
    # 1. Generate all the data
    try:
        # Note: We are unpacking 5 items now
        data = generate_analytics_data(height, width, num_mines, n_boards)
        (white_cell_counts, number_counts, cluster_counts, 
         neighborhood_avg, _) = data # We ignore the 5th item here
    except Exception as e:
        print(f"Error during data generation: {e}")
        return
        
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
    im = ax4.imshow(neighborhood_avg, cmap='Reds', origin='upper')
    ax4.set_title('Average Mine Neighbours Heatmap')
    ax4.set_xlabel('Column')
    ax4.set_ylabel('Row')
    fig.colorbar(im, ax=ax4, label='Average Mines in 3x3 Neighbourhood')
    
    # --- Show the plots ---
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def plot_interactive_analytics(height, width, num_mines, n_boards=1000):
    """
    Generates and saves interactive Plotly graphs as HTML files.
    """
    # 1. Generate all the data
    try:
        data = generate_analytics_data(height, width, num_mines, n_boards)
    except Exception as e:
        print(f"Error during data generation: {e}")
        return
        
    (white_cell_counts, number_counts, cluster_counts, 
     neighborhood_avg, largest_opening_sizes) = data
    
    print("Generating interactive plots...")

    # --- Plot 1: Interactive Histogram of Largest Opening Size ---
    df_openings = pd.DataFrame({
        'Board': list(range(n_boards)),
        'Largest Opening Size': largest_opening_sizes
    })
    
    fig1 = px.histogram(df_openings, x='Largest Opening Size', 
                        title='Histogram of Largest "Opening" Size per Board',
                        labels={'Largest Opening Size': 'Size of Largest "0" Cluster'})
    
    plot1_file = f"interactive_histogram_{height}x{width}x{num_mines}.html"
    fig1.write_html(plot1_file)
    print(f"Saved plot 1 to: {plot1_file}")

    # --- Plot 2: Interactive Scatter Plot (White Cells vs. Clusters) ---
    df_scatter = pd.DataFrame({
        'Board': list(range(n_boards)),
        'White Cells (0s)': white_cell_counts,
        'Mine Clusters': cluster_counts
    })

    fig2 = px.scatter(df_scatter, x='White Cells (0s)', y='Mine Clusters',
                      title='White Cells vs. Mine Clusters (per board)',
                      hover_data=['Board']) # Show Board number on hover
    
    plot2_file = f"interactive_scatter_{height}x{width}x{num_mines}.html"
    fig2.write_html(plot2_file)
    print(f"Saved plot 2 to: {plot2_file}")

    print(f"Interactive plots saved. Open the HTML files in your browser.")

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    print("Testing Analytics Module (Static)...")
    plot_analytics(height=9, width=9, num_mines=10, n_boards=500)
    
    print("Testing Analytics Module (Interactive)...")
    plot_interactive_analytics(height=9, width=9, num_mines=10, n_boards=500)