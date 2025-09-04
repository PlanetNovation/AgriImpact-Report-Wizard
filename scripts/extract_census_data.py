from scripts.download_filtered_table import download_filtered_table
from scripts.get_product_id import get_product_id_by_keyword
from utils.get_data_path import get_data_path
import pandas as pd

def extract_census_data(csv_filename, year: int, progressbar=None, status_label=None, stop_event=None):
    """
    Retrieves all data from the tables
    
    TODO Write documentation for this function
    """
    geo_filter = {"GEO": ["Alberta [PR480000000]"]}
    
    # --- Census of Agriculture Tables to be Downloaded ---
    # Structure: "file_name": "keywords used to find file"
    download_plan = {
        # Farm classifications
        "farm_type": "farm type",
        "total_farm_area": "total farm area",
        "land_tenure": "land tenure",
        "operating_arrangement": "operating arrangement",
        "direct_sales": "direct sales",
        "paid_labour": "paid labour",
        "succession_plan": "succession plan",
        
        # I am not confident these tables are useless but data is currently not being extracted from them
        # "farm_capital": "farm capital",
        # "operating_revenues": "operating revenues",
        # "operating_expenses": "operating expenses"

        # Land & crops
        "land_use": "land use",
        "field_crops": "field crops",
        "fruits": "fruits",
        "greenhouse_products": "greenhouse products",
        "land_inputs": "manure and irrigation",

        # Livestock & poultry
        "cattle_inventory": "cattle inventory",
        "sheep_inventory": "sheep inventory",
        "pig_inventory": "pig inventory",
        "other_livestock": "other livestock inventories",
        "poultry_inventory": "poultry inventories",
        "egg_production": "egg production",
        "bees": "bees",

        # Tech & energy
        "renewable_energy": "renewable energy production",

        # Operators
        "farm_operators_age_sex": "age, sex and number of operators",
        "farm_operators_work": "farm work and other paid work"
    }

    total = len(download_plan)
    completed = 0

    for name, keyword in download_plan.items():
        # Check if user requested stop
        if stop_event and stop_event.is_set():
            if progressbar:
                progressbar['value'] = 0
            if status_label:
                status_label.config(text="⚠️ Download stopped by user")
            return
        
        product_id = get_product_id_by_keyword(csv_filename, keyword)
        if product_id:
            filename = get_data_path(f"{name}_{year}.csv", f"data/{year}")
            
            # Check again before starting a potentially long download
            if stop_event and stop_event.is_set():
                if status_label:
                    status_label.config(text="⚠️ Download stopped by user")
                return
            
            download_filtered_table(product_id, filename, geo_filter, stop_event=stop_event)
            status_text = f"✅ Downloaded {filename}"
        else:
            status_text = f"⚠️ No match found for keyword: {keyword}"
        
        completed += 1
        percent = int((completed / total) * 100)
        
        # update UI if widgets were passed
        if progressbar:
            progressbar['value'] = percent
            progressbar.update_idletasks()
        if status_label:
            status_label.config(text=status_text)
            status_label.update_idletasks()
