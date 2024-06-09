import psutil
import tkinter as tk
from tkinter import font
from GPUtil import getGPUs
import threading
import time

class SystemMonitor(tk.Tk):
	def __init__(self):
		super().__init__()
        self.title("System Monitor")
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.font_style = font.Font(family="Helvetica", size=10)
        self.info_frame = tk.Frame(self, bg="#111")
        self.info_frame.pack(padx=0, pady=0, anchor="w")

        #Die Position des Fensters
        self.startx = 0
        self.starty = 0

        self.close_button = tk.Button(self.info_frame, pady=0, text="✕", font=self.font_style, command=self.destroy, bg="#833", foreground="#fff")
        self.close_button.grid(row=1, column=3, padx=0, pady=0, sticky="e")

        self.last_battery_update = 0
        self.last_network_update = 0

        self.update_stats()

    def add_label(self, text, value, row_num):
        if not hasattr(self, 'labels'):
            self.labels = {}
        if text not in self.labels:
            label = tk.Label(self.info_frame, pady=2, width=10, font=self.font_style, anchor="w", bg="#111", foreground="#eee")
            label.grid(row=row_num, column=0, sticky="w")
            value_label = tk.Label(self.info_frame, width=10, font=self.font_style, anchor="w", bg="#111", foreground="#eee")
            value_label.grid(row=row_num, column=1, sticky="w")
            self.labels[text] = (label, value_label)
        else:
            label, value_label = self.labels[text]
        label.config(text=text)
        value_label.config(text=value)

    def update_stats(self):
        threading.Thread(target=self.update_stats_thread).start()

    def update_stats_thread(self):
        current_time = time.time()

        self.add_label("CPU:", f"{psutil.cpu_percent():02.0f}%", 1)
        self.add_label("Memory:", f"{psutil.virtual_memory().percent:02.0f}%", 2)
        self.add_label("Disk:", f"{psutil.disk_usage('/').percent:02.0f}%", 3)

        # Batteriestatus (1x pro Minute)
        if current_time - self.last_battery_update >= 60:
            battery_status = psutil.sensors_battery()
            if battery_status is not None:
                battery_percent = battery_status.percent
                battery_text = f"{battery_percent:02.0f}%" if battery_percent is not None else "N/A"
                self.add_label("Battery:", battery_text, 6)
                self.last_battery_update = current_time

        # Netzwerk (1x pro Minute)
        if current_time - self.last_network_update >= 60:
            network_usage = psutil.net_io_counters()
            if network_usage is not None:
                upload_speed = network_usage.bytes_sent / 1024 / 1024
                download_speed = network_usage.bytes_recv / 1024 / 1024
                self.add_label("Upload:", f"{upload_speed:03.1f} MB/s", 4)
                self.add_label("Download:", f"{download_speed:03.1f} MB/s", 5)
                self.last_network_update = current_time

        gpus = getGPUs()
        if gpus:
            gpu_info = gpus[0]
            gpu_percent = gpu_info.load * 100
            if gpu_percent is not None:
                self.add_label("GPU:", f"{gpu_percent:05.2f}%", 7)

        window_height = len(self.labels) * 26 + 4
        self.geometry(f"222x{window_height}")

        self.after(1000, self.update_stats_thread)

    def move_window(self, event):
        x = self.winfo_x() - self.startx + event.x
        y = self.winfo_y() - self.starty + event.y
        self.geometry(f"+{x}+{y}")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        snap_distance = 20

        if 0 <= x <= snap_distance and 0 <= y <= snap_distance:
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+0+0")  # Obere linke Ecke
        elif screen_width - snap_distance <= x + self.winfo_width() <= screen_width and 0 <= y <= snap_distance:
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{screen_width - self.winfo_width()}+0")  # Obere rechte Ecke
        elif 0 <= x <= snap_distance and screen_height - snap_distance <= y + self.winfo_height() <= screen_height:
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+0+{screen_height - self.winfo_height()}")  # Untere linke Ecke
        elif screen_width - snap_distance <= x + self.winfo_width() <= screen_width and screen_height - snap_distance <= y + self.winfo_height() <= screen_height:
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{screen_width - self.winfo_width()}+{screen_height - self.winfo_height()}")  # Untere rechte Ecke

    def start_move(self, event):
        self.startx = event.x
        self.starty = event.y

    def stop_move(self, event):
        self.startx = None
        self.starty = None

if __name__ == "__main__":
    app = SystemMonitor()

    app.bind("<ButtonPress-1>", app.start_move)
    app.bind("<ButtonRelease-1>", app.stop_move)
    app.bind("<B1-Motion>", app.move_window)

    app.mainloop()
