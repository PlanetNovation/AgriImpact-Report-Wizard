import tkinter as tk
import itertools
import threading
import time

class TextSpinner(tk.Label):
    def __init__(self, parent, text_prefix="Working...", delay=0.2, **kwargs):
        super().__init__(parent, text="", **kwargs)
        self.text_prefix = text_prefix
        self.delay = delay
        self._stop_event = threading.Event()
        self._thread = None
        self._spinner_cycle = itertools.cycle(["|", "/", "-", "\\"])

    def start(self):
        """Start spinning in a background thread"""
        if self._thread and self._thread.is_alive():
            return  # already running
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop spinning and clear text"""
        self._stop_event.set()
        self.config(text="")

    def _animate(self):
        while not self._stop_event.is_set():
            char = next(self._spinner_cycle)
            self.config(text=f"{self.text_prefix} {char}")
            self.update_idletasks()
            time.sleep(self.delay)