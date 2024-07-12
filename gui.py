import tkinter as tk
from tkinter import ttk
from stopwatch import Stopwatch
import threading
import json

class StopwatchGUI:
    def __init__(self, root):
        self.root = root
        self.stopwatch = Stopwatch()
        self.monitor_thread = None
        self.monitoring = False
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

    def add_tab(self, tab_class, title):
        tab = tab_class(self.notebook, self.stopwatch)
        self.notebook.add(tab.main_frame, text=title)

    def start_stopwatch(self, mode, callback):
        self.status_label.config(text="Status: Running", foreground="green")
        self.split_box.insert(tk.END, f"Started in {mode} mode.\n")
        self.monitoring = True
        self.stopwatch.start()
        self.monitor_thread = threading.Thread(target=callback)
        self.monitor_thread.start()

    def stop_stopwatch(self):
        self.monitoring = False
        self.stopwatch.pause()
        self.status_label.config(text="Status: Stopped", foreground="red")
        if self.monitor_thread:
            self.monitor_thread.join()
        self.split_box.insert(tk.END, "Stopwatch paused.\n")

    def update_splits(self, text):
        self.split_box.insert(tk.END, text)

    def save_statistics(self, mode):
        current_time = self.stopwatch.get_elapsed_time()
        try:
            with open("statistics.json", "r") as f:
                statistics = json.load(f)
        except FileNotFoundError:
            statistics = {}

        if mode not in statistics:
            statistics[mode] = []

        statistics[mode].append(current_time)
        best_time = min(statistics[mode])
        average_time = sum(float(t.split(':')[2]) + 60 * float(t.split(':')[1]) + 3600 * float(t.split(':')[0]) for t in statistics[mode]) / len(statistics[mode])

        print(f"Current Time: {current_time}")
        print(f"Best Time: {best_time}")
        print(f"Average Time: {average_time:.2f}")

        with open("statistics.json", "w") as f:
            json.dump(statistics, f)

        self.split_box.insert(tk.END, f"\nCurrent Time: {current_time}")
        self.split_box.insert(tk.END, f"\nBest Time: {best_time}")
        self.split_box.insert(tk.END, f"\nAverage Time: {average_time:.2f}")
