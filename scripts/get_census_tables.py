import pandas as pd
import requests
from datetime import datetime
from utils.get_data_path import get_data_path

# Returns a list of the past 3 census years based on the current date
def get_last_available_census_years():
    today = datetime.today()
    year = today.year
    latest_census_year = year - ((year - 1) % 5)
    return [latest_census_year - 5*i for i in range(3)]

# Saves a list of the most current census data
# Returns [filename, year] if census data is found, otherwise False
def get_census_tables(status_label=None):
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite"

    try:
        response = requests.get(url, timeout=15)
    except requests.exceptions.Timeout:
        if status_label:
            status_label.config(text="⚠️ Request to Statistics Canada timed out after 15s.")
        return False
    except requests.exceptions.RequestException as e:
        if status_label:
            status_label.config(text=f"⚠️ Failed to connect: {e}")
        return False

    try:
        table_list = response.json()
        df = pd.DataFrame(table_list)
    except Exception as e:
        if status_label:
            status_label.config(text=f"⚠️ Failed to parse census data: {e}")
        return False

    census_years_to_try = get_last_available_census_years()

    # Keywords to filter for just the Agriculture Census tables
    for year in census_years_to_try:
        mask = (
            df['cubeTitleEn'].str.contains("Agriculture", case=False, na=False) &
            df['cubeTitleEn'].str.contains("Census", case=False, na=False) &
            df['cubeTitleEn'].str.contains(str(year), case=False, na=False)
        )
        filtered = df[mask]

        if not filtered.empty:
            filename = get_data_path(f"agriculture_census_tables_{year}.csv", f"data/{year}")
            filtered.to_csv(filename, index=False)

            if status_label:
                status_label.config(text=f"✅ Found census tables for {year}")
            return [filename, year]

    if status_label:
        status_label.config(text="⚠️ No census data found for last 3 census years.")
    return False