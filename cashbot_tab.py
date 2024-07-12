import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import cv2
from PIL import ImageGrab
import pytesseract
import threading
import numpy as np
import json
import time

class CashbotTab:
    def __init__(self, root, stopwatch):
        self.root = root
        self.stopwatch = stopwatch
        self.main_frame = ttk.Frame(root)
        self.mode_var = tk.StringVar()
        self.monitor_thread = None
        self.monitoring = False
        self.floor_detected = False
        self.in_battle = False
        self.battle_count = 0
        self.time_started = False  # Add this flag
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.main_frame, text="Select Mode:").grid(row=0, column=0)
        mode_menu = ttk.Combobox(self.main_frame, textvariable=self.mode_var)
        mode_menu['values'] = ['Coin', 'Dollar', 'Bullion', 'CFO']
        mode_menu.grid(row=0, column=1)

        start_button = ttk.Button(self.main_frame, text="Start", command=self.start_stopwatch)
        start_button.grid(row=1, column=0, columnspan=2)

        stop_button = ttk.Button(self.main_frame, text="Stop", command=self.stop_stopwatch)
        stop_button.grid(row=2, column=0, columnspan=2)

        self.status_label = ttk.Label(self.main_frame, text="Status: Idle", foreground="black")
        self.status_label.grid(row=3, column=0, columnspan=2)

        self.split_box = ScrolledText(self.main_frame, width=40, height=10)
        self.split_box.grid(row=4, column=0, columnspan=2)

    def start_stopwatch(self):
        mode = self.mode_var.get()
        if mode:
            self.status_label.config(text="Status: Running", foreground="green")
            self.split_box.delete('1.0', tk.END)  # Clear the split box
            self.split_box.insert(tk.END, f"Started in {mode} mode.\n")
            self.monitoring = True
            self.floor_detected = False
            self.in_battle = False
            self.battle_count = 0
            self.time_started = False  # Reset the flag
            self.stopwatch.reset()  # Reset the stopwatch to 0
            self.monitor_thread = threading.Thread(target=self.monitor_game, args=(mode,))
            self.monitor_thread.start()

    def stop_stopwatch(self):
        self.monitoring = False
        self.stopwatch.pause()
        self.status_label.config(text="Status: Stopped", foreground="red")
        if self.monitor_thread:
            self.monitor_thread.join()
        self.split_box.insert(tk.END, "Stopwatch paused.\n")

    def monitor_game(self, mode):
        bbox = (930, 320, 1180, 380)  # Correct values to capture the text region
        shticker_book_img = cv2.imread('images/shtickerbook.png', 0)
        factory_end_img = cv2.imread('images/mintend.png', 0)

        if mode == 'CFO':
            cfo_start_img = cv2.imread('images/cfostart.png', 0)
            cfo_end_img = cv2.imread('images/cfoend.png', 0)
            cfo_crane_img = cv2.imread('images/cfocrane.png', 0)

        while self.monitoring:
            screenshot = ImageGrab.grab()
            open_cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

            if mode != 'CFO' and not self.floor_detected:
                floor_text = pytesseract.image_to_string(gray_screen[bbox[1]:bbox[3], bbox[0]:bbox[2]])
                print(f"OCR Result: {floor_text}")

                if "floor" in floor_text.lower():
                    try:
                        floor_number = int(floor_text.split("floor:")[1].split()[0])
                        if floor_number == 0:
                            floor_number = 1
                        elif floor_number == 19:
                            floor_number = 20
                        self.split_box.insert(tk.END, f"Detected Floor: {floor_number}\n")
                        self.floor_detected = True
                        if not self.time_started:
                            self.stopwatch.start()  # Start counting time only now
                            self.time_started = True  # Set the flag
                    except (IndexError, ValueError) as e:
                        self.split_box.insert(tk.END, "Error parsing floor number.\n")
                        print(f"Error parsing floor number: {e}")
                else:
                    self.split_box.insert(tk.END, "Could not detect floor number.\n")

            if mode == 'CFO':
                res_start = cv2.matchTemplate(gray_screen, cfo_start_img, cv2.TM_CCOEFF_NORMED)
                loc_start = np.where(res_start >= 0.8)

                if len(loc_start[0]) > 0 and not self.time_started:
                    self.stopwatch.start()  # Start the stopwatch
                    self.time_started = True  # Set the flag
                    self.split_box.insert(tk.END, "CFO Start detected. Stopwatch started.\n")
                    self.split_box.see(tk.END)  # Scroll to the end

                res_crane = cv2.matchTemplate(gray_screen, cfo_crane_img, cv2.TM_CCOEFF_NORMED)
                loc_crane = np.where(res_crane >= 0.8)

                if len(loc_crane[0]) > 0 and self.time_started and not self.in_battle:
                    self.in_battle = True
                    self.battle_count += 1
                    split_name = f"cfocrane {self.battle_count}"
                    split_time = self.stopwatch.record_split(split_name)
                    if split_time:
                        self.split_box.insert(tk.END, f"{split_name} split: {split_time}\n")
                    self.split_box.see(tk.END)  # Scroll to the end

                elif len(loc_crane[0]) == 0 and self.in_battle:
                    self.in_battle = False

                res_end = cv2.matchTemplate(gray_screen, cfo_end_img, cv2.TM_CCOEFF_NORMED)
                loc_end = np.where(res_end >= 0.8)

                if len(loc_end[0]) > 0 and self.time_started:
                    self.monitoring = False
                    self.stopwatch.pause()
                    self.status_label.config(text="Status: Stopped", foreground="red")
                    self.split_box.insert(tk.END, "End of CFO detected. Stopwatch paused.\n")
                    current_time = self.stopwatch.get_elapsed_time()
                    self.split_box.insert(tk.END, f"Final Time: {current_time}\n")
                    self.split_box.see(tk.END)  # Scroll to the end
                    self.save_statistics(mode, current_time)
                    break

            else:
                res_battle = cv2.matchTemplate(gray_screen, shticker_book_img, cv2.TM_CCOEFF_NORMED)
                loc_battle = np.where(res_battle >= 0.8)

                if len(loc_battle[0]) > 0 and self.floor_detected and not self.in_battle:
                    self.in_battle = True
                    self.battle_count += 1
                    split_name = f"Battle {self.battle_count}"
                    split_time = self.stopwatch.record_split(split_name)
                    if split_time:
                        self.split_box.insert(tk.END, f"{split_name} split: {split_time}\n")
                    self.split_box.see(tk.END)  # Scroll to the end

                elif len(loc_battle[0]) == 0 and self.in_battle:
                    self.in_battle = False

                res_end = cv2.matchTemplate(gray_screen, factory_end_img, cv2.TM_CCOEFF_NORMED)
                loc_end = np.where(res_end >= 0.8)

                if len(loc_end[0]) > 0:
                    self.monitoring = False
                    self.stopwatch.pause()
                    self.status_label.config(text="Status: Stopped", foreground="red")
                    self.split_box.insert(tk.END, "End of Mint Detected. Stopwatch paused.\n")
                    current_time = self.stopwatch.get_elapsed_time()
                    self.split_box.insert(tk.END, f"Final Time: {current_time}\n")
                    self.split_box.see(tk.END)  # Scroll to the end
                    self.save_statistics(mode, current_time)
                    break

            time.sleep(1)

    def save_statistics(self, mode, current_time):
        try:
            with open("cashbot_statistics.json", "r") as f:
                statistics = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            statistics = {"best_times": {}, "run_times": {}}

        if "run_times" not in statistics:
            statistics["run_times"] = {}
        if "best_times" not in statistics:
            statistics["best_times"] = {}

        if mode not in statistics["run_times"]:
            statistics["run_times"][mode] = []

        try:
            h, m, s = map(float, current_time.split(':'))
            total_seconds = h * 3600 + m * 60 + s
        except ValueError:
            print(f"Skipping invalid time format: {current_time}")
            return

        statistics["run_times"][mode].append(total_seconds)

        if mode not in statistics["best_times"]:
            statistics["best_times"][mode] = total_seconds
        else:
            statistics["best_times"][mode] = min(statistics["best_times"][mode], total_seconds)

        with open("cashbot_statistics.json", "w") as f:
            json.dump(statistics, f, indent=4)

        best_time = statistics["best_times"][mode]
        average_time = sum(statistics["run_times"][mode]) / len(statistics["run_times"][mode])
        average_time_str = time.strftime('%H:%M:%S', time.gmtime(average_time))

        self.split_box.insert(tk.END, f"\nBest Time: {time.strftime('%H:%M:%S', time.gmtime(best_time))}")
        self.split_box.insert(tk.END, f"\nAverage Time: {average_time_str}")
        self.split_box.see(tk.END)  # Scroll to the end

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Toontown Stopwatch")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    from stopwatch import Stopwatch
    stopwatch = Stopwatch()

    cashbot_tab = CashbotTab(notebook, stopwatch)
    notebook.add(cashbot_tab.main_frame, text="Cashbot")

    root.mainloop()
