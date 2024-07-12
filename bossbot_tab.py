import tkinter as tk
from tkinter import ttk
from stopwatch import Stopwatch

class BossbotTab:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#32CD32")
        self.mode_var = tk.StringVar(value="First Fairway")

        self.create_controls()

    def create_controls(self):
        mode_frame = ttk.Frame(self.frame)
        mode_frame.pack(fill=tk.X, pady=10)

        mode_label = ttk.Label(mode_frame, text="Select Mode:")
        mode_label.pack(side=tk.LEFT, padx=5)

        mode_menu = ttk.Combobox(mode_frame, textvariable=self.mode_var)
        mode_menu['values'] = ["First Fairway", "Final Fringe", "CEO"]
        mode_menu.pack(side=tk.LEFT, padx=5)

        length_label = ttk.Label(mode_frame, text="Select Length:")
        length_label.pack(side=tk.LEFT, padx=5)

        self.length_var = tk.StringVar(value="Minimal")
        length_menu = ttk.Combobox(mode_frame, textvariable=self.length_var)
        length_menu['values'] = ["Minimal", "Full"]
        length_menu.pack(side=tk.LEFT, padx=5)

        start_button = ttk.Button(self.frame, text="Start", command=self.start_stopwatch)
        start_button.pack(pady=5)

        stop_button = ttk.Button(self.frame, text="Stop", command=self.stop_stopwatch)
        stop_button.pack(pady=5)

        self.status_label = ttk.Label(self.frame, text="Status: Idle", font=("Helvetica", 14, "bold"), foreground="black")
        self.status_label.pack(pady=10)

        self.splits_frame = ttk.Frame(self.frame, padding="5", relief=tk.SUNKEN)
        self.splits_frame.pack(fill=tk.BOTH, expand=True)

        splits_label = ttk.Label(self.splits_frame, text="Splits")
        splits_label.pack()

        self.splits_text = tk.Text(self.splits_frame, height=10, width=50, state=tk.DISABLED, background="black", foreground="white", font=("Helvetica", 10))
        self.splits_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.stopwatch = Stopwatch(self.update_callback)

    def update_callback(self, message):
        self.splits_text.config(state=tk.NORMAL)
        self.splits_text.insert(tk.END, message + "\n")
        self.splits_text.see(tk.END)
        self.splits_text.config(state=tk.DISABLED)

    def start_stopwatch(self):
        mode = self.mode_var.get()
        length = self.length_var.get()
        self.status_label.config(text="Status: Running", foreground="green")
        self.splits_text.config(state=tk.NORMAL)
        self.splits_text.delete(1.0, tk.END)
        self.splits_text.config(state=tk.DISABLED)
        self.stopwatch.start()

    def stop_stopwatch(self):
        self.stopwatch.stop()
        self.status_label.config(text="Status: Stopped", foreground="red")
