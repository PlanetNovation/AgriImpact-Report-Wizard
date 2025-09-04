import os
import sys

def get_data_path(filename, folder="data"):
    """
    Returns a path to a file inside the given folder relative to the project root.
    Creates the data folder if it doesn't exist.

    Parameters:
        filename (str): Name of file
        folder (str, optional): Folder name relative to project root. Defaults to 'data'

    Returns:
        str: Full path to the file
    """
    # Checks if project is running as an executable or script
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script: go up from scripts/ to project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.abspath(os.path.join(script_dir, ".."))  # project root
    
    # Normalize the folder string (handles 'data/2021' properly)
    folder = os.path.normpath(folder)
    folder_path = os.path.join(base_dir, folder)

    # Ensure folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Full file path
    full_path = os.path.join(folder_path, filename)

    # Normalize separators in final path
    return os.path.normpath(full_path)
