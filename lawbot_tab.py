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

class LawbotTab:
    def __init__(self, root, stopwatch):
        self.root = root
        self.stopwatch = stopwatch
        self.main_frame = ttk.Frame(root)
        self.mode_var = tk.StringVar()
        self.monitor_thread = None
        self.monitoring = False
        self.floor_detected = False
        self.last_floor_number = None
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.main_frame, text="Select Mode:").grid(row=0, column=0)
        mode_menu = ttk.Combobox(self.main_frame, textvariable=self.mode_var)
        mode_menu['values'] = ['Junior', 'Senior', 'CJ']
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
            self.last_floor_number = None
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
        bbox = (930, 320, 1180, 380)  # Corrected bounding box values
        office_end_img = cv2.imread('images/mintend.png', 0)

        while self.monitoring:
            screenshot = ImageGrab.grab()
            open_cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_screen = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

            floor_text = pytesseract.image_to_string(gray_screen[bbox[1]:bbox[3], bbox[0]:bbox[2]])
            print(f"OCR Result: {floor_text}")

            # Handle OCR misinterpretations
            floor_text = floor_text.lower().replace('o', '0').replace('i', '1').replace('fl00r', 'floor').replace('f100r', 'floor')
            print(f"Debug: Corrected OCR Result: {floor_text}")

            parts = floor_text.replace(':', ' ').split()
            print(f"Debug: OCR Text Parts: {parts}")

            if 'floor' in parts:
                try:
                    floor_index = parts.index('floor') + 1
                    floor_number = int(parts[floor_index])

                    if self.last_floor_number != floor_number:
                        self.split_box.insert(tk.END, f"Detected Floor: {floor_number}\n")
                        split_name = f"Floor {floor_number}"
                        split_time = self.stopwatch.record_split(split_name)
                        if split_time:
                            self.split_box.insert(tk.END, f"{split_name} split: {split_time}\n")
                        self.split_box.see(tk.END)  # Scroll to the end
                        self.last_floor_number = floor_number

                except (IndexError, ValueError) as e:
                    print(f"Error parsing floor number: {e}")

            res_end = cv2.matchTemplate(gray_screen, office_end_img, cv2.TM_CCOEFF_NORMED)
            loc_end = np.where(res_end >= 0.8)

            if len(loc_end[0]) > 0:
                self.monitoring = False
                self.stopwatch.pause()
                self.status_label.config(text="Status: Stopped", foreground="red")
                self.split_box.insert(tk.END, "End of Office Detected. Stopwatch paused.\n")
                current_time = self.stopwatch.get_elapsed_time()
                self.split_box.insert(tk.END, f"Final Time: {current_time}\n")
                self.split_box.see(tk.END)  # Scroll to the end
                self.save_statistics(mode, current_time)
                break

            time.sleep(1)

    def save_statistics(self, mode, current_time):
        try:
            with open("lawbot_statistics.json", "r") as f:
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

        with open("lawbot_statistics.json", "w") as f:
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

    lawbot_tab = LawbotTab(notebook, stopwatch)
    notebook.add(lawbot_tab.main_frame, text="Lawbot")

    root.mainloop()
