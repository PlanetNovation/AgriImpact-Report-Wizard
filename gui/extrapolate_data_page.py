import ttkbootstrap as ttk
import threading
from gui.text_spinner import TextSpinner
from scripts.import_recent_census_data import import_recent_census_data

def create_import_frame(parent, wizard, stop_event):
    frame = ttk.Frame(parent)
    
    # Container to hold all widgets and center them
    container = ttk.Frame(frame)
    container.place(relx=0.5, rely=0.5, anchor="center")

    # Title
    title_label = ttk.Label(container, text="Extrapolate Data", font=("Segoe UI", 30, "bold"))
    title_label.pack(pady=(0, 45))  # space below the title

    # Status label
    status_label = ttk.Label(container, text="Ready to import...")
    status_label.pack(pady=5)

    # Progress bar
    progress = ttk.Progressbar(container, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    # Spinner
    spinner = TextSpinner(container)
    spinner.pack(pady=5)

    # Start button
    start_btn = ttk.Button(container, text="Start Import")
    start_btn.pack(pady=10)

    # Cancel button
    cancel_btn = ttk.Button(container, text="Cancel Import", bootstyle="danger")
    cancel_btn.pack(pady=5)
    cancel_btn.config(state="disabled")

    # --- Button logic ---
    def start_import():
        stop_event.clear()
        start_btn.config(state="disabled")
        cancel_btn.config(state="normal")
        spinner.start()
        status_label.config(text="Importing recent census data...")
        progress['value'] = 0

        def task():
            try:
                # Early exit if already cancelled
                if stop_event.is_set():
                    status_label.config(text="⚠️ Import stopped before start")
                    return

                # Run your import function
                import_recent_census_data(status_label=status_label,wizard=wizard , stop_event=stop_event)

                # If cancelled during import
                if stop_event.is_set():
                    status_label.config(text="⚠️ Import cancelled by user")
                    progress['value'] = 0
                else:
                    status_label.config(text="✅ Import complete!")
            except Exception as e:
                status_label.config(text=f"❌ Error: {e}")
            finally:
                spinner.stop()
                start_btn.config(state="normal")
                cancel_btn.config(state="disabled")

        threading.Thread(target=task, daemon=True).start()

    def cancel_import():
        stop_event.set()
        progress['value'] = 0
        status_label.config(text="⚠️ Import cancelling...")
        # The actual cancel will happen inside import_recent_census_data if it checks stop_event
        spinner.stop()
        start_btn.config(state="normal")
        cancel_btn.config(state="disabled")

    start_btn.config(command=start_import)
    cancel_btn.config(command=cancel_import)

    return frame