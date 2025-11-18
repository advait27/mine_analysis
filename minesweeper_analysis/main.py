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
    Main Menu for Minesweeper:
    - Preset difficulties (Easy/Intermediate/Expert)
    - NEW: Custom Game
    - NEW: Custom Analytics
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper - Main Menu")
        self.root.geometry("320x350")
        self.root.resizable(False, False)

        title_label = tk.Label(
            self.root, text="Minesweeper", font=("Arial", 24, "bold")
        )
        title_label.pack(pady=15)

        button_frame = tk.Frame(self.root)
        button_frame.pack()

        # --- Preset Game Modes ---
        easy_button = tk.Button(
            button_frame,
            text="Easy (9x9, 10 Mines)",
            width=25,
            command=lambda: self.start_game(9, 9, 10),
        )
        easy_button.pack(pady=5)

        intermediate_button = tk.Button(
            button_frame,
            text="Intermediate (16x16, 40 Mines)",
            width=25,
            command=lambda: self.start_game(16, 16, 40),
        )
        intermediate_button.pack(pady=5)

        expert_button = tk.Button(
            button_frame,
            text="Expert (16x30, 99 Mines)",
            width=25,
            command=lambda: self.start_game(16, 30, 99),
        )
        expert_button.pack(pady=5)

        # --- NEW: Custom Game Mode ---
        custom_button = tk.Button(
            button_frame,
            text="Custom Game (Choose Size)",
            width=25,
            command=self.custom_game_dialog,
        )
        custom_button.pack(pady=15)

        # --- Analytics Button ---
        analytics_button = tk.Button(
            button_frame,
            text="Run Analytics",
            width=25,
            command=self.custom_analytics_dialog,
        )
        analytics_button.pack(pady=10)

        if not ANALYTICS_ENABLED:
            analytics_button.config(state=tk.DISABLED, text="Analytics (disabled)")

    # --------------------------
    # Start Game with parameters
    # --------------------------
    def start_game(self, height, width, mines):
        self.root.withdraw()
        game_window = tk.Toplevel(self.root)
        MinesweeperGUI(game_window, height, width, mines)
        game_window.protocol(
            "WM_DELETE_WINDOW", lambda: self.on_game_close(game_window)
        )

    def on_game_close(self, game_window):
        game_window.destroy()
        self.root.deiconify()

    # --------------------------
    # Custom Game Dialog
    # --------------------------
    def custom_game_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Game Settings")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Custom Board Size", font=("Arial", 12, "bold")).pack(
            pady=10
        )

        tk.Label(dialog, text="Height:").pack()
        height_entry = tk.Entry(dialog)
        height_entry.pack()

        tk.Label(dialog, text="Width:").pack()
        width_entry = tk.Entry(dialog)
        width_entry.pack()

        tk.Label(dialog, text="Mines:").pack()
        mines_entry = tk.Entry(dialog)
        mines_entry.pack()

        def start_custom_game():
            try:
                h = int(height_entry.get())
                w = int(width_entry.get())
                m = int(mines_entry.get())

                if h <= 0 or w <= 0:
                    raise ValueError("Dimensions must be > 0")
                if m <= 0 or m >= h * w:
                    raise ValueError("Invalid number of mines")

                dialog.destroy()
                self.start_game(h, w, m)

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter valid integers.\n"
                    "Mines must be less than total cells.",
                )

        tk.Button(dialog, text="Start Game", command=start_custom_game).pack(pady=15)

    # --------------------------
    # Custom Analytics Dialog
    # --------------------------
    def custom_analytics_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Analytics Settings")
        dialog.geometry("300x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(
            dialog, text="Analytics Configuration", font=("Arial", 12, "bold")
        ).pack(pady=10)

        tk.Label(dialog, text="Height:").pack()
        height_entry = tk.Entry(dialog)
        height_entry.insert(0, "9")
        height_entry.pack()

        tk.Label(dialog, text="Width:").pack()
        width_entry = tk.Entry(dialog)
        width_entry.insert(0, "9")
        width_entry.pack()

        tk.Label(dialog, text="Mines:").pack()
        mines_entry = tk.Entry(dialog)
        mines_entry.insert(0, "10")
        mines_entry.pack()

        tk.Label(dialog, text="Number of Boards (n):").pack(pady=5)
        n_entry = tk.Entry(dialog)
        n_entry.insert(0, "1000")
        n_entry.pack()

        def run_custom_analytics():
            try:
                h = int(height_entry.get())
                w = int(width_entry.get())
                m = int(mines_entry.get())
                n = int(n_entry.get())

                if h <= 0 or w <= 0:
                    raise ValueError("Dimensions must be > 0")
                if m <= 0 or m >= h * w:
                    raise ValueError("Invalid number of mines")
                if n <= 0:
                    raise ValueError("n must be > 0")

                dialog.destroy()
                self.root.withdraw()

                messagebox.showinfo(
                    "Analytics Running",
                    f"Generating {n} boards...\nThis may take a moment.",
                )

                analytics.plot_analytics(h, w, m, n)

                messagebox.showinfo("Analytics Complete", "Plots are ready.")

                self.root.deiconify()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(dialog, text="Run Analytics", command=run_custom_analytics).pack(
            pady=20
        )


# --- Main code to run the application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
