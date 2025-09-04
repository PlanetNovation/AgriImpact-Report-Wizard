from scripts.get_statcan_value import get_statcan_value
from utils.wizard_data import WizardData

# TODO: Move to WizardData class

def import_recent_census_data(status_label=None, wizard=None, stop_event=None):
    """
    Updates the wizard_state.json data to the most recently pulled agriculture census data.
    Supports cancellation via stop_event.
    """
    for item_name, fields in wizard.data.get("items", {}).items():
        # ✅ Check stop_event before starting each item
        if stop_event and stop_event.is_set():
            if status_label:
                status_label.config(text="⚠️ Import stopped by user")
            break

        # Skip if the item is marked as not included
        if not fields.get("included", False):
            continue

        file_keyword = fields.get("file_keyword")
        name_keywords = fields.get("name_keywords", [])
        unit_of_measure = fields.get("unit_of_measure")

        # Skip items missing config
        if not file_keyword or not name_keywords or not unit_of_measure:
            continue

        # Try to pull the StatCan value
        result = get_statcan_value(
            file_keyword=file_keyword,
            name_keywords=name_keywords,
            unit_of_measure=unit_of_measure
        )

        if stop_event and stop_event.is_set():
            if status_label:
                status_label.config(text="⚠️ Import stopped by user")
            break

        if result:
            wizard.extrapolate_value(
                item_name=item_name,
                provincial_value=result["value"],
                status=result["status"]
            )
            if status_label:
                status_label.config(text=f"✅ Processed {item_name} ({result['year']})")
        else:
            if status_label:
                status_label.config(text=f"⚠️ No data found for {item_name}")
