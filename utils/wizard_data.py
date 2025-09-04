import json
import os
import math
from datetime import datetime
from utils.get_data_path import get_data_path  # optional: if you want to save JSON in your data folder
from utils.default_wizard_state import get_default_wizard_state
from utils.to_native import to_native

class WizardData:
    """
    Class to manage the wizard state
    """
    def __init__(self, filename="wizard_state.json"):
        self.filename = get_data_path(filename, "state")  # saves inside project-root/data
        self.data = {}
        self.load()

    # Old methods that shouldnt be needed anymore TODO: Ensure these methods are not required
    # def set(self, key, value):
    #     self.data[key] = value
    #     self.save()

    # def get(self, key, default=None):
    #     return self.data.get(key, default)

    # def set_field(self, key, field_name, value):
    #     record = self.data.get(key, {})
    #     record[field_name] = value
    #     self.set(key, record)

    # def get_field(self, key, field_name, default=None):
    #     return self.data.get(key, {}).get(field_name, default)
    
    def get_item_field(self, item_name, field_name, default=None):
        """
        Retrieve a specific field from an item in `items`.
        
        Example:
            get_item_field("gross farm receipts", "method")
        """
        return (
            self.data.get("items", {})
            .get(item_name, {})
            .get(field_name, default)
        )
    
    def set_item_field(self, item_name, field_name, value):
        """
        Set a specific field in an item under `items`.

        Example:
            set_item_field("gross farm receipts", "method", "calculated from StatsCan table XYZ")
        """
        # Convert pandas/numpy scalars to native
        value = to_native(value)
        
        # Ensure "items" exists
        if "items" not in self.data:
            self.data["items"] = {}

        # Ensure the item exists
        if item_name not in self.data["items"]:
            self.data["items"][item_name] = {}
            
        # Convert bad JSON values
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            value = None

        # Set the field value
        self.data["items"][item_name][field_name] = value

        # Persist to file
        self.save()


    def save(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w") as f:
            json.dump(self.data, f)

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        else:
            self.data = get_default_wizard_state()
            self.save()

    def save_to_history(self, item_name):
        """
        Snapshots the current item values and saves them to the history list,
        but only if:
        1. a valid value exists
        2. its different from the most recent history entry
        """
        value = to_native(self.get_item_field(item_name=item_name, field_name="value"))
        method = self.get_item_field(item_name=item_name, field_name="method")
        date_gathered = self.get_item_field(item_name=item_name, field_name="date")

        # Skip if value is None or NaN
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return

        history = self.get_item_field(item_name=item_name, field_name="history", default=[])

        new_entry = {
            "value": value,
            "method": method,
            "date_gathered": date_gathered,
            "date_saved_to_history": datetime.today().date().isoformat()
        }

        # Check against last entry to avoid duplicates
        if history and all(
            new_entry.get(k) == history[-1].get(k)
            for k in ("value", "method", "date_gathered")
        ):
            return  # No change, skip saving

        # Save new history entry
        history.append(new_entry)
        self.set_item_field(item_name, "history", history)
        
    def extrapolate_value(self, item_name, provincial_value, status):
        """
        Takes in the provincial value and applies the SE Alberta ratio.
        If provincial_value is missing/None, does nothing.
        """
        # Bail early if no provincial value provided
        if provincial_value is None or provincial_value == "":
            return  # do nothing
        
        # Convert to native (handles numpy/pandas scalars)
        provincial_value = to_native(provincial_value)
        
        # Bail if provincial_value is NaN/Inf
        if isinstance(provincial_value, float) and (math.isnan(provincial_value) or math.isinf(provincial_value)):
            return
        
        # Get ratio safely
        ratio = self.get_item_field(item_name=item_name, field_name="ratio")
        if ratio is None:
            return  # do nothing

        try:
            provincial_value = float(provincial_value)
            ratio = float(ratio)
        except (TypeError, ValueError):
            return  # invalid number, do nothing
    
        # Bail if ratio is NaN/Inf
        if math.isnan(ratio) or math.isinf(ratio):
            return
        
        # Save current snapshot to history
        self.save_to_history(item_name=item_name)

        # Apply ratio
        se_alberta_value = round(provincial_value * ratio)

        # Data to be overridden
        fields = {
            "value": se_alberta_value,
            "method": "extrapolation",
            "date_value_was_applied": datetime.today().date().isoformat(),
            "quality": status
        }

        # Override current data
        for field, data in fields.items():
            self.set_item_field(item_name=item_name, field_name=field, value=data)