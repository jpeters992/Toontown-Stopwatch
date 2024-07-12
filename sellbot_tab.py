import tkinter as tk
from tkinter import ttk
import cv2
from PIL import ImageGrab
import threading
import numpy as np
import json
import time

class SellbotTab:
    def __init__(self, root, stopwatch):
        self.root = root
        self.stopwatch = stopwatch
        self.main_frame = ttk.Frame(root)
        self.mode_var = tk.StringVar()
        self.monitor_thread = None
        self.monitoring = False
        self.in_battle = False
        self.battle_count = 0
        self.factory_started = False  # Add a flag for factory start
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.main_frame, text="Select Mode:").grid(row=0, column=0)
        mode_menu = ttk.Combobox(self.main_frame, textvariable=self.mode_var)
        mode_menu['values'] = ['Factory6', 'Factory12', 'VP']
        mode_menu.grid(row=0, column=1)

        start_button = ttk.Button(self.main_frame, text="Start", command=self.start_stopwatch)
        start_button.grid(row=1, column=0, columnspan=2)

        stop_button = ttk.Button(self.main_frame, text="Stop", command=self.stop_stopwatch)
        stop_button.grid(row=2, column=0, columnspan=2)

        self.status_label = ttk.Label(self.main_frame, text="Status: Idle", foreground="black")
        self.status_label.grid(row=3, column=0, columnspan=2)

        self.split_box = tk.Text(self.main_frame, width=40, height=10)
        self.split_box.grid(row=4, column=0, columnspan=2)

        # Adding a scrollbar to the split box
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.split_box.yview)
        self.split_box['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=4, column=2, sticky='ns')

    def start_stopwatch(self):
        mode = self.mode_var.get()
        if mode:
            self.split_box.delete('1.0', tk.END)  # Clear the console
            self.status_label.config(text="Status: Running", foreground="green")
            self.insert_text(f"Started in {mode} mode.\n")
            self.monitoring = True
            self.in_battle = False
            self.battle_count = 0
            self.factory_started = False  # Reset the factory start flag
            self.stopwatch.reset()  # Reset the stopwatch when starting a new run
            self.stopwatch.start()
            self.monitor_thread = threading.Thread(target=self.monitor_game, args=(mode,))
            self.monitor_thread.start()

    def stop_stopwatch(self):
        self.monitoring = False
        self.stopwatch.pause()
        self.stopwatch.reset()  # Reset the stopwatch
        self.status_label.config(text="Status: Stopped", foreground="red")
        if self.monitor_thread:
            self.monitor_thread.join()
        self.insert_text("Stopwatch paused.\n")

    def monitor_game(self, mode):
        factory_start_img = cv2.imread('images/start.png', 0)
        factory_end_img = cv2.imread('images/factoryend.png', 0)
        shticker_book_img = cv2.imread('images/shtickerbook.png', 0)
        
        vp_start_img = cv2.imread('images/vpstart.png', 0)
        vp_end_img = cv2.imread('images/vpend.png', 0)
        skelecog_img = cv2.imread('images/skelecog.png', 0)
        pie_round_img = cv2.imread('images/pieround.png', 0)

        while self.monitoring:
            screenshot = ImageGrab.grab()
            open_cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

            if mode in ['Factory6', 'Factory12']:
                # Start of factory detection
                if not self.factory_started:
                    res_start = cv2.matchTemplate(gray_screen, factory_start_img, cv2.TM_CCOEFF_NORMED)
                    loc_start = np.where(res_start >= 0.8)  # Adjust the threshold as needed

                    if len(loc_start[0]) > 0:
                        self.factory_started = True  # Set the flag to true
                        split_name = "Factory Start"
                        self.insert_text(f"Entering {split_name}\n")
                        split_time = self.stopwatch.record_split(split_name)
                        if split_time:
                            self.insert_text(f"{split_name} split: {split_time}\n")

                # In-battle detection
                res_battle = cv2.matchTemplate(gray_screen, shticker_book_img, cv2.TM_CCOEFF_NORMED)
                loc_battle = np.where(res_battle >= 0.8)  # Adjust the threshold as needed

                if len(loc_battle[0]) > 0 and not self.in_battle:
                    self.in_battle = True
                    self.battle_count += 1
                    self.insert_text(f"Entering Battle {self.battle_count}\n")
                elif len(loc_battle[0]) == 0 and self.in_battle:
                    split_name = f"Battle {self.battle_count}"
                    self.insert_text(f"Exiting {split_name}\n")
                    split_time = self.stopwatch.record_split(split_name)
                    if split_time:
                        self.insert_text(f"{split_name} split: {split_time}\n")
                    self.in_battle = False

                # End of factory detection
                res_end = cv2.matchTemplate(gray_screen, factory_end_img, cv2.TM_CCOEFF_NORMED)
                loc_end = np.where(res_end >= 0.8)  # Adjust the threshold as needed

                if len(loc_end[0]) > 0:
                    self.monitoring = False
                    self.stopwatch.pause()
                    self.status_label.config(text="Status: Stopped", foreground="red")
                    self.insert_text("End of Factory Detected. Stopwatch paused.\n")
                    current_time = self.stopwatch.get_elapsed_time()
                    self.insert_text(f"Final Time: {current_time}\n")
                    self.save_statistics(mode)
                    break

            elif mode == 'VP':
                # Start of VP detection
                if not self.factory_started:
                    res_start = cv2.matchTemplate(gray_screen, vp_start_img, cv2.TM_CCOEFF_NORMED)
                    loc_start = np.where(res_start >= 0.8)  # Adjust the threshold as needed

                    if len(loc_start[0]) > 0:
                        self.factory_started = True  # Set the flag to true
                        split_name = "VP Start"
                        self.insert_text(f"Entering {split_name}\n")
                        split_time = self.stopwatch.record_split(split_name)
                        if split_time:
                            self.insert_text(f"{split_name} split: {split_time}\n")

                # Skelecog round detection
                res_skelecog = cv2.matchTemplate(gray_screen, skelecog_img, cv2.TM_CCOEFF_NORMED)
                loc_skelecog = np.where(res_skelecog >= 0.8)  # Adjust the threshold as needed

                if len(loc_skelecog[0]) > 0 and not self.in_battle:
                    split_name = "Skelecog Round"
                    self.insert_text(f"Entering {split_name}\n")
                    split_time = self.stopwatch.record_split(split_name)
                    if split_time:
                        self.insert_text(f"{split_name} split: {split_time}\n")
                    self.in_battle = True

                # Pie round detection
                res_pie = cv2.matchTemplate(gray_screen, pie_round_img, cv2.TM_CCOEFF_NORMED)
                loc_pie = np.where(res_pie >= 0.8)  # Adjust the threshold as needed

                if len(loc_pie[0]) > 0 and self.in_battle:
                    split_name = "Pie Round"
                    self.insert_text(f"Entering {split_name}\n")
                    split_time = self.stopwatch.record_split(split_name)
                    if split_time:
                        self.insert_text(f"{split_name} split: {split_time}\n")
                    self.in_battle = False

                # End of VP detection
                res_end = cv2.matchTemplate(gray_screen, vp_end_img, cv2.TM_CCOEFF_NORMED)
                loc_end = np.where(res_end >= 0.8)  # Adjust the threshold as needed

                if len(loc_end[0]) > 0:
                    self.monitoring = False
                    self.stopwatch.pause()
                    self.status_label.config(text="Status: Stopped", foreground="red")
                    self.insert_text("End of VP Detected. Stopwatch paused.\n")
                    current_time = self.stopwatch.get_elapsed_time()
                    self.insert_text(f"Final Time: {current_time}\n")
                    self.save_statistics(mode)
                    break

            time.sleep(1)

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

        self.insert_text(f"\nCurrent Time: {current_time}")
        self.insert_text(f"\nBest Time: {best_time}")
        self.insert_text(f"\nAverage Time: {average_time:.2f}")

    def insert_text(self, text):
        self.split_box.insert(tk.END, text)
        self.split_box.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Toontown Stopwatch")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    from stopwatch import Stopwatch
    stopwatch = Stopwatch()

    sellbot_tab = SellbotTab(notebook, stopwatch)
    notebook.add(sellbot_tab.main_frame, text="Sellbot")

    root.mainloop()
