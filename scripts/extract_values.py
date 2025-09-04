import json
from utils.get_data_path import get_data_path

def extract_values():
    # Get the path to the wizard_state.json file
    filepath = get_data_path("wizard_state.json", "state")

    # Load the JSON file
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract key => value mapping only if "included" is True
    values_dict = {
        key: item.get("value")
        for key, item in data.get("items", {}).items()
        if item.get("included") is True
    }

    return values_dict