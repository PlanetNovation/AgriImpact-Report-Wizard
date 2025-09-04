import ttkbootstrap as ttk
import threading
import csv
from datetime import datetime
from utils.get_data_path import get_data_path
from gui.text_spinner import TextSpinner

def create_export_frame(parent, stop_event):
    frame = ttk.Frame(parent)

    # Container to center everything
    container = ttk.Frame(frame)
    container.place(relx=0.5, rely=0.5, anchor="center")

    # Title
    title_label = ttk.Label(container, text="Export Wizard Data", font=("Segoe UI", 30, "bold"))
    title_label.pack(pady=(0, 45))

    # Status label
    status_label = ttk.Label(container, text="Ready to export...")
    status_label.pack(pady=5)

    # Progress bar
    progress = ttk.Progressbar(container, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    # Spinner
    spinner = TextSpinner(container)
    spinner.pack(pady=5)

    # Export button
    export_btn = ttk.Button(container, text="Export to Excel")
    export_btn.pack(pady=10)

    # Cancel button
    cancel_btn = ttk.Button(container, text="Cancel Export", bootstyle="danger")
    cancel_btn.pack(pady=5)
    cancel_btn.config(state="disabled")

    # --- Button callbacks ---
    def start_export():
        stop_event.clear()
        export_btn.config(state="disabled")
        cancel_btn.config(state="normal")
        spinner.start()
        status_label.config(text="Exporting data...")
        progress['value'] = 0

        def task():
            try:
                # Load the wizard_state.json
                state_file = get_data_path("wizard_state.json", folder="state")
                import json
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                items = data.get("items", {})

                # --- Always use current year ---
                year = datetime.now().year

                # --- Destination file ---
                export_filename = f"statscan_wizard_export_{year}.csv"
                export_file = get_data_path(export_filename, folder="exports")

                # Write CSV
                with open(export_file, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    # Header row
                    writer.writerow(["Name", "Value", "Unit of Measure", "Category"])
                    
                    total = len(items)
                    for idx, (key, item) in enumerate(items.items(), start=1):
                        if stop_event.is_set():
                            status_label.config(text="⚠️ Export stopped by user!")
                            progress['value'] = 0
                            spinner.stop()
                            export_btn.config(state="normal")
                            cancel_btn.config(state="disabled")
                            return

                        writer.writerow([
                            item.get("title", key),
                            item.get("value"),
                            item.get("unit_of_measure") or "",
                            item.get("category") or ""
                        ])
                        progress['value'] = (idx / total) * 100

                status_label.config(text=f"✅ Export complete! Saved to {export_file}")
            except Exception as e:
                status_label.config(text=f"❌ Export failed: {e}")
            finally:
                spinner.stop()
                export_btn.config(state="normal")
                cancel_btn.config(state="disabled")

        threading.Thread(target=task, daemon=True).start()

    def cancel_export():
        progress['value'] = 0
        stop_event.set()
        status_label.config(text="⚠️ Export cancelled by user")
        spinner.stop()
        export_btn.config(state="normal")
        cancel_btn.config(state="disabled")

    export_btn.config(command=start_export)
    cancel_btn.config(command=cancel_export)

    return frame