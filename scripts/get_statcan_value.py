import os
import re
import pandas as pd
from utils.get_data_path import get_data_path
from utils.to_native import to_native

def get_statcan_value(file_keyword, name_keywords, unit_of_measure, data_folder="data"):
    """
    Search for the most recent StatsCan CSV file containing file_keyword,
    filter by name_keywords + unit_of_measure, and return VALUE, STATUS, and folder year.

    Parameters:
        file_keyword (str): keyword to find the correct file (e.g., "bees")
        name_keywords (list[str]): exact match keywords (punctuation/case ignored)
        unit_of_measure (str): exact match required for Unit of measure (or UOM if fallback)
        data_folder (str): root folder containing year subfolders

    Returns:
        dict or None: { "value": ..., "status": ..., "year": ... }
    """
    
    # Get all year folders under data/, sorted descending (most recent first)
    year_folders = sorted(
        [f for f in os.listdir(get_data_path("", data_folder)) if f.isdigit()],
        key=int,
        reverse=True
    )
    
    target_file = None
    year_used = None

    # Find the most recent matching file
    for year in year_folders:
        year_path = get_data_path("", os.path.join(data_folder, year))
        for fname in os.listdir(year_path):
            if file_keyword.lower() in fname.lower() and fname.endswith(".csv"):
                target_file = get_data_path(fname, os.path.join(data_folder, year))
                year_used = year
                break
        if target_file:
            break

    if not target_file:
        raise FileNotFoundError(f"No file with keyword '{file_keyword}' found in {data_folder}")

    # Load the file
    df = pd.read_csv(target_file)

    # Identify the "name" column (first non-standard one)
    standard_cols = {"REF_DATE", "GEO", "DGUID", "Unit of measure", "UOM", "VALUE", "STATUS"}
    name_col = next((c for c in df.columns if c not in standard_cols), None)
    if not name_col:
        raise ValueError("Could not identify a name column in file")

    # Pick unit of measure column
    if "Unit of measure" in df.columns:
        uom_col = "Unit of measure"
    elif "UOM" in df.columns:
        uom_col = "UOM"
    else:
        raise ValueError("No Unit of measure or UOM column found")

    # --- Normalize for case + punctuation insensitive comparison ---
    def normalize(text):
        if pd.isna(text):
            return ""
        return re.sub(r"[^\w\s]", "", str(text)).lower().strip()

    df["_normalized_name"] = df[name_col].map(normalize)
    normalized_keywords = [normalize(kw) for kw in name_keywords]

    # Only match rows where ALL keywords appear in the normalized name
    def row_matches_keywords(name):
        return all(kw in name for kw in normalized_keywords)

    mask = df["_normalized_name"].apply(row_matches_keywords)


    # Filter by UOM
    mask &= df[uom_col] == unit_of_measure

    filtered = df[mask]

    if filtered.empty:
        return None

    # Take first match (or expand later to return all)
    row = filtered.iloc[0]

    return {
        "value": to_native(row["VALUE"]),
        "status": to_native(row["STATUS"]),
        "year": to_native(year_used)
    }