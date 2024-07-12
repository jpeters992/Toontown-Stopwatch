import tkinter as tk
from gui import StopwatchGUI
from cashbot_tab import CashbotTab
from sellbot_tab import SellbotTab

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Toontown Stopwatch")

    app = StopwatchGUI(root)

    app.add_tab(CashbotTab, "Cashbot")
    app.add_tab(SellbotTab, "Sellbot")

    # Add other tabs similarly:
    # app.add_tab(LawbotTab, "Lawbot")
    # app.add_tab(BossbotTab, "Bossbot")

    root.mainloop()
