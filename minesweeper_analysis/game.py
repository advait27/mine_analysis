import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  
from board import Board
import numpy as np
import highscore_manager as hs   

class MinesweeperGUI:
    
    def __init__(self, root, height=9, width=9, num_mines=10):
        self.root = root
        self.height = height
        self.width = width
        self.num_mines = num_mines
    
        self.config_key = f"{height}x{width}x{num_mines}"

        self.color_map = {
            1: "blue", 2: "green", 3: "red", 4: "purple",
            5: "maroon", 6: "turquoise", 7: "black", 8: "gray"
        }
        self.root.title("Minesweeper")
        self.root.resizable(False, False)

        # --- Create UI Frames ---
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(pady=5)
        self.grid_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.grid_frame.pack(padx=10, pady=10)

        # --- Header Widgets ---
        self.mine_label = tk.Label(self.header_frame, text=f"Mines: {self.num_mines:03d}", 
                                   font=("Arial", 14, "bold"), width=9)
        self.mine_label.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(self.header_frame, text="😊", font=("Arial", 16), 
                                      width=3, command=self.new_game)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        self.timer_label = tk.Label(self.header_frame, text="Time: 000", 
                                    font=("Arial", 14, "bold"), width=9)
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.highscore_button = tk.Button(self.header_frame, text="🏆", font=("Arial", 16), 
                                          width=3, command=self.show_highscores)
        self.highscore_button.pack(side=tk.LEFT, padx=10)

        self.new_game()

    def new_game(self):
        self.game_over = False
        self.first_click = True
        self.mines_left = self.num_mines
        self.timer_seconds = 0
        self.timer_id = None
        
        self.mine_label.config(text=f"Mines: {self.mines_left:03d}")
        self.timer_label.config(text="Time: 000")
        self.reset_button.config(text="😊")
        
        # Stop any lingering timer
        self.stop_timer() 

        self.board = Board(self.height, self.width, self.num_mines)
        
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        for r in range(self.height):
            row_list = []
            for c in range(self.width):
                btn = tk.Button(self.grid_frame, width=2, height=1,
                                relief=tk.RAISED, bg="#ddd")
                btn.bind("<Button-1>", lambda e, r=r, c=c: self.on_left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.on_right_click(r, c, e))
                btn.bind("<Button-2>", lambda e, r=r, c=c: self.on_right_click(r, c, e), add="+")
                btn.grid(row=r, column=c)
                row_list.append(btn)
            self.buttons.append(row_list)

    def on_left_click(self, r, c):
        if self.game_over:
            return
        if self.board.player_view[r, c] == -2:
            return
        if self.board.player_view[r, c] >= 0:
            return

        if self.first_click:
            while self.board.board[r, c] == -9:
                self.board = Board(self.height, self.width, self.num_mines)
            self.first_click = False
            self.start_timer()

        val = self.board.board[r, c]
        if val == -9:
            self.game_over_lose(r, c)
        else:
            self.reveal_cell(r, c)
            self.check_win()

    def on_right_click(self, r, c, event=None):
        """
        Handles the right-click event to flag/unflag a cell.
        r, c: coordinates of the button.
        event: The event object (required by bind).
        """
        
        if self.game_over:
            return
        btn = self.buttons[r][c]
        # If the cell is already revealed (>= 0), stop.
        if self.board.player_view[r, c] >= 0:
            return
        if self.board.player_view[r, c] >= 0:
            return
        # If the cell is HIDDEN (-1) -> Flag it
        if self.board.player_view[r, c] == -1:
            self.board.player_view[r, c] = -2
            btn.config(text="🚩",fg="red", bg="light yellow" )
            self.mines_left -= 1
        elif self.board.player_view[r, c] == -2:
            self.board.player_view[r, c] = -1
            btn.config(text="",fg="black", bg="#ddd")
            self.mines_left += 1
        self.mine_label.config(text=f"Mines: {self.mines_left:03d}")

    def reveal_cell(self, r, c):
        if not (0 <= r < self.height and 0 <= c < self.width):
            return
        if self.board.player_view[r, c] >= 0:
            return
        if self.board.player_view[r, c] == -2:
            return
            
        val = self.board.board[r, c]
        self.board.player_view[r, c] = val
        self.update_button_appearance(r, c)

        if val == 0:
            for i in range(max(0, r - 1), min(self.height, r + 2)):
                for j in range(max(0, c - 1), min(self.width, c + 2)):
                    if (i, j) == (r, c):
                        continue
                    self.reveal_cell(i, j)

    def update_button_appearance(self, r, c):
        val = self.board.player_view[r, c]
        btn = self.buttons[r][c]
        
        btn.config(relief=tk.SUNKEN, bg="light gray", state=tk.DISABLED) 
       
        if val == 0:
            btn.config(text="")
        elif val > 0:
            btn.config(text=str(val), fg=self.color_map.get(val, "black"))
    
    def game_over_lose(self, r_clicked, c_clicked):
        self.game_over = True
        self.stop_timer()
        self.reset_button.config(text="😵")
        
        for r in range(self.height):
            for c in range(self.width):
                if self.board.board[r, c] == -9:
                    if (r, c) == (r_clicked, c_clicked):
                        self.buttons[r][c].config(text="💣", bg="red")
                    elif self.board.player_view[r, c] == -2:
                         self.buttons[r][c].config(text="🚩", bg="green")
                    else:
                        self.buttons[r][c].config(text="💣", bg="#eee")
        
        messagebox.showinfo("Game Over", "You clicked on a mine!")
        
    def check_win(self):
        revealed_count = np.sum(self.board.player_view >= 0)
        total_non_mines = (self.height * self.width) - self.num_mines
        
        if not self.game_over and revealed_count == total_non_mines:
            self.game_over = True
            self.stop_timer()
            self.reset_button.config(text="😎")
            
            self.mine_label.config(text="Mines: 000")
            for r in range(self.height):
                for c in range(self.width):
                    if self.board.board[r, c] == -9:
                        self.buttons[r][c].config(text="🚩", bg="#ccc")
           
            self.handle_win_highscore()

    def handle_win_highscore(self):
        """
        Called on a win. Checks if the time is a highscore,
        and if so, asks for the player's name and saves the score.
        """
        time = self.timer_seconds
        
        if hs.is_highscore(self.config_key, time):
            # It's a highscore! Ask for name.
            name = simpledialog.askstring("New Highscore!", 
                                          "You got a highscore!\nEnter your name:",
                                          parent=self.root)
            
            if name: # User entered a name and clicked OK
                hs.add_score(self.config_key, name, time)
                win_message = f"Congratulations, {name}!\nYour time: {time}s"
                # Show the highscore list after they win
                self.show_highscores(show_message_after=win_message)
            else: # User clicked Cancel
                win_message = f"Congratulations!\nYour time: {time}s\n(Score not saved)"
                messagebox.showinfo("You Win!", win_message)

        else:
            # Not a highscore
            messagebox.showinfo("You Win!", f"Congratulations!\nYour time: {self.timer_seconds}s")
            
    def show_highscores(self, show_message_after=None):
        """
        Displays a messagebox with the highscores for the
        current board configuration.
        """
        # If this was called from a win, show the win message first
        if show_message_after:
            messagebox.showinfo("You Win!", show_message_after)

        scores = hs.get_scores(self.config_key)
        
        if not scores:
            message = "No highscores for this level yet."
        else:
            message = f"Top {hs.MAX_SCORES} for {self.config_key}\n\n"
            for i, (name, time) in enumerate(scores):
                message += f"{i+1}. {name} - {time}s\n"
                
        # The 'parent=self.root' makes the messagebox appear over the game
        messagebox.showinfo("Highscores", message, parent=self.root)

    # --- Timer Functions ---
    def start_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        self.timer_seconds = 0
        self.timer_label.config(text="Time: 000")
        self.update_timer()
        
    def update_timer(self):
        if self.game_over:
            return
        self.timer_label.config(text=f"Time: {self.timer_seconds:03d}")
        self.timer_seconds += 1
        self.timer_id = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

# --- Main code to run the game ---
if __name__ == "__main__":
    root = tk.Tk()
    game = MinesweeperGUI(root, height=9, width=9, num_mines=10)
    root.mainloop()