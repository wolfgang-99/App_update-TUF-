import tkinter as tk
from tkinter.ttk import Progressbar

class ProgressWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("App Update")
        self.window.geometry("400x200")
        self.progress_bar = Progressbar(self.window, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(pady=20)
        self.status_label = tk.Label(self.window, text="Initializing update...", font=("Arial", 14))
        self.status_label.pack(pady=20)
        self.complete = False

    def update(self, progress: int):
        if progress >= 100:
            self.status_label.config(text="Update Complete!")
            self.progress_bar['value'] = 100
            self.complete = True
        else:
            self.progress_bar['value'] = progress
            self.status_label.config(text=f"Updating... {progress}%")
        self.window.update_idletasks()

    def close(self):
        self.window.destroy()


def progress_hook(progress_window: ProgressWindow, progress: int):
    progress_window.update(progress)

