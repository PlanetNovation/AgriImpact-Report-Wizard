import ttkbootstrap as ttk
import threading
from gui.text_spinner import TextSpinner
from scripts.get_census_tables import get_census_tables
from scripts.extract_census_data import extract_census_data

def create_extract_frame(parent, stop_event):
    frame = ttk.Frame(parent)
    
    # Container to hold all widgets and center them
    container = ttk.Frame(frame)
    container.place(relx=0.5, rely=0.5, anchor="center")  # center horizontally & vertically

    # Title
    title_label = ttk.Label(container, text="Import Recent Census Data", font=("Segoe UI", 30, "bold"))
    title_label.pack(pady=(0, 45))  # space below the title

    # Status labels
    status_label = ttk.Label(container, text="Ready to start...")
    status_label.pack(pady=5)

    # Progress bar
    progress = ttk.Progressbar(container, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    # Spinner
    spinner = TextSpinner(container)
    spinner.pack(pady=5)

    # Start button
    start_btn = ttk.Button(container, text="Start Download")
    start_btn.pack(pady=10)
    
    # Cancel button
    cancel_btn = ttk.Button(container, text="Cancel Download", bootstyle="danger")  # bright red
    cancel_btn.pack(pady=5)
    cancel_btn.config(state="disabled")


    # Button callback
    def start_download():
        stop_event.clear() # Allow a new download
        start_btn.config(state="disabled")   # disable button
        cancel_btn.config(state="normal")
        spinner.start()                      # start spinner
        status_label.config(text="Fetching latest census tables...")
        progress['value'] = 0

        def task():
            # Check stop_event before doing anything
            if stop_event.is_set():
                spinner.stop()
                start_btn.config(state="normal")
                return
            
            result = get_census_tables(status_label=status_label)
            
            # Check if the user requested stop first
            if stop_event and stop_event.is_set():
                status_label.config(text="⚠️ Download stopped by user!")
                progress['value'] = 0
                spinner.stop()
                start_btn.config(state="normal")
                cancel_btn.config(state="disabled")
                return

            # Check if census tables were not found
            if not result:
                progress['value'] = 0
                spinner.stop()
                start_btn.config(state="normal")
                cancel_btn.config(state="disabled")
                return

            census_tables, year = result
            extract_census_data(census_tables, year, progress, status_label, stop_event)

            if not stop_event.is_set():
                status_label.config(text="✅ All downloads complete!")
            spinner.stop()
            start_btn.config(state="normal")
            cancel_btn.config(state="disabled")

        threading.Thread(target=task, daemon=True).start()
        
    def cancel_download():
        progress['value'] = 0
        stop_event.set()
        status_label.config(text="⚠️ Download cancelled by user")
        spinner.stop()  # if using spinner
        start_btn.config(state="normal")
        cancel_btn.config(state="disabled")

    start_btn.config(command=start_download)
    cancel_btn.config(command=cancel_download)

    return frame