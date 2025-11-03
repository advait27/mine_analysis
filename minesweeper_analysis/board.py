import numpy as np
import random

class Board:
    """
    Represents the Minesweeper game board.
    
    This class handles the creation of the board, placement of mines,
    and calculation of numbers for each cell.
    
    Attributes:
        height (int): The height of the board (number of rows).
        width (int): The width of the board (number of columns).
        num_mines (int): The total number of mines on the board.
        board (np.ndarray): A 2D numpy array representing the "solution" board.
                            -9 represents a mine.
                            0-8 represents the number of adjacent mines.
        player_view (np.ndarray): A 2D numpy array representing the player's view.
                            -1 represents a hidden cell.
                            -2 represents a marked (flagged) cell.
                            0-8 represents a revealed cell.
    """
    
    def __init__(self, height, width, num_mines):
        """
        Initializes the Board object.

        Args:
            height (int): The number of rows.
            width (int): The number of columns.
            num_mines (int): The number of mines.
        """
        self.height = height
        self.width = width
        self.num_mines = num_mines
        
        # Solution board: -9 for mine, 0-8 for numbers
        self.board = np.zeros((height, width), dtype=int)
        
        # Player's view: -1 for hidden, -2 for marked, 0-8 for revealed
        self.player_view = np.full((height, width), -1, dtype=int)
        
        self._place_mines()
        self._calculate_numbers()

    def _place_mines(self):
        """
        Internal method to randomly place mines on the board.
        Mines are represented by -9.
        """
        # Get a flat list of all possible (row, col) coordinates
        all_coords = [(r, c) for r in range(self.height) for c in range(self.width)]
        
        # Randomly choose 'num_mines' coordinates
        mine_coords = random.sample(all_coords, self.num_mines)
        
        # Place mines on the board
        for r, c in mine_coords:
            self.board[r, c] = -9 # -9 indicates a mine

    def _calculate_numbers(self):
        """
        Internal method to calculate the numbers for all non-mine cells.
        Each number represents the count of adjacent mines.
        """
        for r in range(self.height):
            for c in range(self.width):
                # Skip if this cell is a mine
                if self.board[r, c] == -9:
                    continue
                
                # Count adjacent mines
                mine_count = 0
                # Iterate over all 8 neighbors (and the cell itself)
                for i in range(max(0, r - 1), min(self.height, r + 2)):
                    for j in range(max(0, c - 1), min(self.width, c + 2)):
                        # Don't count the cell itself
                        if (i, j) == (r, c):
                            continue
                        # Check if the neighbor is a mine
                        if self.board[i, j] == -9:
                            mine_count += 1
                
                self.board[r, c] = mine_count

    def print_board_solution(self):
        """Helper function to print the solution (for debugging)."""
        print("--- Solution Board ---")
        for r in range(self.height):
            row_str = ""
            for c in range(self.width):
                if self.board[r, c] == -9:
                    row_str += " * "
                else:
                    row_str += f" {self.board[r, c]} "
            print(row_str)

    def print_player_view(self):
        """Helper function to print the player's current view (for debugging)."""
        print("--- Player View ---")
        for r in range(self.height):
            row_str = ""
            for c in range(self.width):
                val = self.player_view[r, c]
                if val == -1:
                    row_str += " . " # Hidden
                elif val == -2:
                    row_str += " F " # Flagged/Marked
                else:
                    row_str += f" {val} " # Revealed number
            print(row_str)

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # This part only runs when you execute this file directly
    
    print("Testing Easy Board (9x9, 10 mines)")
    easy_board = Board(height=9, width=9, num_mines=10)
    easy_board.print_board_solution()
    
    print("\n" + "="*30 + "\n")
    
    print("Testing Player View (all hidden)")
    easy_board.print_player_view()