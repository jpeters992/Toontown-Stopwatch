import tkinter as tk
from tkinter import ttk
from stopwatch import Stopwatch
from sellbot_tab import SellbotTab
from cashbot_tab import CashbotTab
from lawbot_tab import LawbotTab

class ToontownStopwatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Toontown Stopwatch")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.stopwatch = Stopwatch()

        self.create_tabs()

    def create_tabs(self):
        # Sellbot tab
        sellbot_tab = SellbotTab(self.notebook, self.stopwatch)
        self.notebook.add(sellbot_tab.main_frame, text="Sellbot")

        # Cashbot tab
        cashbot_tab = CashbotTab(self.notebook, self.stopwatch)
        self.notebook.add(cashbot_tab.main_frame, text="Cashbot")

        # Lawbot tab
        lawbot_tab = LawbotTab(self.notebook, self.stopwatch)
        self.notebook.add(lawbot_tab.main_frame, text="Lawbot")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToontownStopwatchApp(root)
    root.mainloop()
