import tkinter as tk
from tkinter import messagebox, simpledialog
from game import MinesweeperGUI

# Try to import the analytics module
try:
    import analytics
    ANALYTICS_ENABLED = True
except ImportError as e:
    print(f"Could not import analytics: {e}")
    print("Analytics feature will be disabled.")
    print("Please install 'matplotlib', 'scipy', 'plotly', and 'pandas' to enable it.")
    ANALYTICS_ENABLED = False

class MainMenu:
    """
    This class creates the main menu for the Minesweeper application.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper - Main Menu")
        self.root.geometry("300x250")
        self.root.resizable(False, False)

        title_label = tk.Label(self.root, text="Minesweeper", font=("Arial", 24, "bold"))
        title_label.pack(pady=15)

        button_frame = tk.Frame(self.root)
        button_frame.pack()

        # --- Game Mode Buttons ---
        easy_button = tk.Button(button_frame, text="Easy (9x9, 10 Mines)", 
                                width=25, command=lambda: self.start_game(9, 9, 10))
        easy_button.pack(pady=5)

        intermediate_button = tk.Button(button_frame, text="Intermediate (16x16, 40 Mines)", 
                                        width=25, command=lambda: self.start_game(16, 16, 40))
        intermediate_button.pack(pady=5)

        expert_button = tk.Button(button_frame, text="Expert (16x30, 99 Mines)", 
                                  width=25, command=lambda: self.start_game(16, 30, 99))
        expert_button.pack(pady=5)

        # --- Analytics Button ---
        analytics_button = tk.Button(button_frame, text="Run Analytics", 
                                     width=25, command=self.run_analytics_dialog)
        analytics_button.pack(pady=15)
        if not ANALYTICS_ENABLED:
            analytics_button.config(state=tk.DISABLED, text="Analytics (disabled)")


    def start_game(self, height, width, mines):
        self.root.withdraw()
        game_window = tk.Toplevel(self.root)
        game_gui = MinesweeperGUI(game_window, height, width, mines)
        game_window.protocol("WM_DELETE_WINDOW", lambda: self.on_game_close(game_window))

    def on_game_close(self, game_window):
        game_window.destroy()
        self.root.deiconify()

    def run_analytics_dialog(self):
        """
        Shows a popup to get analytics settings from the user.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Analytics Settings")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.grab_set() # Make window modal
        
        tk.Label(dialog, text="Board Configuration").pack(pady=5)
        
        # --- Config selection ---
        config_var = tk.StringVar(dialog)
        config_var.set("Easy (9x9, 10)") # Default value
        
        configs = {
            "Easy (9x9, 10)": (9, 9, 10),
            "Intermediate (16x16, 40)": (16, 16, 40),
            "Expert (16x30, 99)": (16, 30, 99)
        }
        
        option_menu = tk.OptionMenu(dialog, config_var, *configs.keys())
        option_menu.pack(pady=5)
        
        # --- Number of boards ---
        tk.Label(dialog, text="Number of Boards to Simulate (n):").pack(pady=5)
        n_boards_entry = tk.Entry(dialog, width=15)
        n_boards_entry.insert(0, "1000") # Default value
        n_boards_entry.pack(pady=5)
        
        def on_run():
            try:
                h, w, m = configs[config_var.get()]
                n = int(n_boards_entry.get())
                
                if n <= 0:
                    raise ValueError("Number of boards must be > 0")
                
                dialog.destroy()
                self.root.withdraw()
                
                messagebox.showinfo("Running Analytics",
                                    f"Starting analytics for {n} boards.\n"
                                    "This may take a moment.\n"
                                    "Plots will appear when finished.",
                                    parent=self.root)
                
                # --- Run Both Plotting Functions ---
                
                # 1. Run the original static plots
                print("Running static plots...")
                analytics.plot_analytics(h, w, m, n)
                
                # 2. Run the new interactive plots
                print("Running interactive plots...")
                analytics.plot_interactive_analytics(h, w, m, n)
                
                # --- Show Final Message ---
                messagebox.showinfo("Analytics Complete",
                                    "Static plots shown.\n"
                                    "Interactive plots saved to HTML files in the program folder.",
                                    parent=self.root)
                
                self.root.deiconify()
                
            except ValueError:
                messagebox.showerror("Invalid Input", 
                                     "Number of boards must be a valid integer > 0.",
                                     parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}", parent=dialog)
                self.root.deiconify()

        # --- Run Button ---
        run_button = tk.Button(dialog, text="Run", command=on_run)
        run_button.pack(pady=20)

# --- Main code to run the application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()