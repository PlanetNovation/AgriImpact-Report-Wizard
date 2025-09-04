import requests
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
import time
from utils.get_data_path import get_data_path
from threading import Event

def download_filtered_table(table_id: int, output_file: str, filters: dict, stop_event: Event = None, timeout: int = 15) -> dict:
    """
    Downloads a table from Statistics Canada, extracts to CSV, applies filters, saves to data folder.
    Can be safely stopped using stop_event.

    Parameters:
        table_id (int): StatCan table ID (Ex: 32100309) **WITHOUT VARIATION**
        output_file (str): Name of output file
        filters (dict): Dictionary of filters (Ex: {"GEO": ["Alberta"]})
        stop_event (threading.Event, optional): Event to signal stopping the download
        timeout (int): Timeout in seconds for HTTP requests

    Returns:
        dict: {
            "success": bool,
            "error": str | None,
            "details": str | None
        }
    """
    result = {"success": False, "error": None, "details": None}

    try:
        # Early exit if stop requested
        if stop_event and stop_event.is_set():
            result["error"] = "Download stopped by user."
            return result

        # Step 1: Get CSV download JSON object
        url = f"https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{table_id}/en"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        time.sleep(0.04)

        if stop_event and stop_event.is_set():
            result["error"] = "Download stopped by user."
            return result

        data = response.json()

        # Step 2: Extract ZIP URL
        zip_url = data.get("object")
        if not zip_url:
            result["error"] = "Missing 'object' field in StatCan response."
            result["details"] = f"Response JSON: {data}"
            return result

        if stop_event and stop_event.is_set():
            result["error"] = "Download stopped by user."
            return result

        # Step 3: Download the ZIP file
        zip_file = requests.get(zip_url, timeout=timeout)
        zip_file.raise_for_status()
        time.sleep(0.04)

        if stop_event and stop_event.is_set():
            result["error"] = "Download stopped by user."
            return result

        # Step 4: Extract CSV
        with ZipFile(BytesIO(zip_file.content)) as z:
            csv_files = [f for f in z.namelist() if f.endswith(".csv") and "MetaData" not in f]
            if not csv_files:
                result["error"] = "No valid CSV found in ZIP."
                result["details"] = f"Files in ZIP: {z.namelist()}"
                return result
            csv_filename = csv_files[0]
            df = pd.read_csv(z.open(csv_filename))

        if stop_event and stop_event.is_set():
            result["error"] = "Download stopped by user."
            return result

        # Step 5: Apply filters
        df_filtered = df.copy()
        for key, value in filters.items():
            if stop_event and stop_event.is_set():
                result["error"] = "Download stopped by user."
                return result
            if key not in df_filtered.columns:
                result["details"] = (result["details"] or "") + f" Warning: Column '{key}' not found."
                continue
            df_filtered = df_filtered[df_filtered[key].isin(value)]

        if stop_event and stop_event.is_set():
            result["error"] = "Download stopped by user."
            return result

        # Step 6: Save filtered results
        output_path = get_data_path(output_file)
        df_filtered.to_csv(output_path, index=False)

        result["success"] = True
        return result

    except requests.exceptions.Timeout:
        result["error"] = "Request timed out."
    except requests.exceptions.RequestException as e:
        result["error"] = f"HTTP error: {e}"
    except ValueError:
        result["error"] = "Failed to parse JSON."
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"

    return result
