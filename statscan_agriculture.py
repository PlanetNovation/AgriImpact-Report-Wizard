from gui.sidebar_navigator import SidebarNavigator
from gui.edit_page import create_edit_frame
from gui.extract_data_page import create_extract_frame
from gui.extrapolate_data_page import create_import_frame
from utils.wizard_data import WizardData
import ttkbootstrap as ttk
import threading

def main():
    wizard = WizardData("wizard_state.json")

    root = ttk.Window(themename="flatly")
    root.title("AgriImpact Report Wizard")
    root.geometry("1000x600")
    
    # Create stop event for threads
    stop_event = threading.Event()
    
    # Bind close button to safely stop threads
    def on_close():
        stop_event.set()  # signal all threads to stop
        root.destroy()    # then close the window
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    # Define the pages
    pages = {
        "Extract Data": lambda parent: create_extract_frame(parent, stop_event=stop_event),
        "Extrapolate Data": lambda parent: create_import_frame(parent, wizard, stop_event=stop_event),
        "Edit Data": lambda parent: create_edit_frame(parent, wizard.data),
        "Create Stats Table": lambda parent: ttk.Label(parent, text="Create Stats Table Page", font=("Segoe UI", 14)),
        "Review Table": lambda parent: ttk.Label(parent, text="Review Table Page", font=("Segoe UI", 14)),
        "Create Report": lambda parent: ttk.Label(parent, text="Create Report Page", font=("Segoe UI", 14)),
        "Append Report": lambda parent: ttk.Label(parent, text="Append Report Page", font=("Segoe UI", 14)),
        "Export": lambda parent: ttk.Label(parent, text="Export Page", font=("Segoe UI", 14)),
        "Documentation": lambda parent: ttk.Label(parent, text="Documentation Page", font=("Segoe UI", 14))
    }

    # Add the sidebar navigator
    nav = SidebarNavigator(root, pages)
    nav.pack(fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
