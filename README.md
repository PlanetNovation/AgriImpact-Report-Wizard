# Economic Impact Report Wizard

This tool aids in the generation of the Economic Impact of Southeast Alberta by gathering the most recent agriculture census data.

# Project Overview

The system is designed to:
- Retrieve the latest agricultural census data
- Filter for relevant statistics
- Extrapolate the data
- Present the findings while displaying how accurate the data is

# Data Source

All data is gathered from [Statistics Canada](https://www150.statcan.gc.ca/n1/en/type/data?MM=1).

# TODO: Setup Instructions

### 1. Install Python

Download and install Python 3.13.5 or later from [python.org](https://www.python.org/downloads/).  

If running from a portable environment (such as a USB), ensure that the full Python path is used explicitly in all commands. Or you might need to run the following command like I did:
```
set PATH=E:\Python-3.13.5;%PATH%
```

### 2. Install Dependencies

Run the following using your Python executable (modify the path as necessary):
```
E:\Python-3.13.5\python.exe -m pip install -r requirements.txt
```

This will install all of the required packages.

### 3. Run the Script

This will:
- Download and filter data from StatsCan
- Output a filtered CSV (Alberta only, 2024)
- Generate a plain text output suitable for copying into reports

### Dependency Management

Dependencies are locked to specific versions via `requirements.txt` to ensure consistency.

To update the list manually:
```
E:\Python-3.13.5\python.exe -m pip freeze > requirements.txt
```

# Usage
TODO: Finish

# Project Structure

```
project-root/
├── data/                       # CSV imports and intermediate datasets
├── gui/                        # GUI scripts
├── outputs/                    # Final processed CSVs
├── scripts/                    # Python scripts for data access and transformation
├── state/
│   └── wizard_state.json       # Acts as the system's database - contains all report data and wizard state 
├── utils/                      # Utility scripts
├── .gitignore
├── requirements.txt            # List of pinned dependencies
├── README.md                   # This documentation file
└── statcan_agriculture.py     # Primary entry point for the program
```

# Data Structure

The file [wizard_state.json](./state/wizard_state.json) is the central "database" for the system. It has two main sections:
- `items` → the core dataset used for building the report
- `meta` → state information for the wizard interface

## Top-level Structure
```
{
  "items": {
    "number of farms with renewable energy": { ... },
    "number of farms with solar panels": { ... },
    "number of farms with wind turbines": { ... },
    "number of farm operators": { ... }
  },
  "meta": {
    "last_page": "Extract Data",
    "last_run": null
  }
}
```

## `items` Schema

| Field Name               | Type             | Description / Purpose                                                           | Example                                                        |
| ------------------------ | ---------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `value`                  | int/float/null   | The most recent numeric value used in the report. May be `null` if not yet set. | `12345`                                                        |
| `title`                  | str              | Human-readable label for the item.                                              | `"Number of farms with renewable energy"`                      |
| `description`            | str              | Additional notes or context for the item.                                       | `"Estimated number of farms reporting renewable energy use"`   |
| `method`                 | str/null         | How the value was derived: `"user"`, `"direct"`, `"extrapolated"`, or `"old"`.  | `"extrapolated"`                                               |
| `date_value_was_applied` | str (ISO) / null | Date when this value/method was last applied.                                   | `"2025-08-13"`                                                 |
| `ratio`                  | float/null       | Extrapolation ratio applied to derive SE Alberta values.                        | `0.06`                                                         |
| `ratio_last_updated`     | str (ISO) / null | Last date the ratio was updated.                                                | `"2025-08-13"`                                                 |
| `quality`                | str/null         | Indicator of data quality (e.g., `"actual"`, `"estimated"`, `"low"`).           | `"estimated"`                                                  |
| `category`               | str              | Logical grouping of the item for display and reporting.                         | `"Sustainability"`                                             |
| `included`               | bool             | Whether the item should be included in outputs and calculations.                | `true`                                                         |
| `file_keyword`           | str/null         | Keyword used to locate the appropriate StatsCan CSV file.                       | `"renewable"`                                                  |
| `name_keywords`          | list\[str]       | Keywords required to match a specific row within the StatsCan file.             | `["production", "total"]`                                      |
| `unit_of_measure`        | str/null         | Exact match required for the “Unit of measure” column in StatsCan files. Defaults to UOM column if "Unit of measure" column is not found | `"Number of farms reporting"`                                  |
| `history`                | list             | Prior values and metadata for auditability.                                     | `[{"value": 12000, "method": "direct", "date": "2024-05-01"}]` |

## `meta` Schema (Experimental)

The `meta` object is intended to store wizard session state.  
⚠️ Currently unused — subject to change in future versions.

# Maintenance Guide (What Might Break)
TODO: Finish



# Extending the System (How to add, change, or remove fields/features)
TODO: Finish

#### Many of these customization options are planned to be moved to a more permanent solution. Information can be found in [Future Plans](#future-plans).

## Adding/Removing a Category on "Edit Page" Section

To change a category simply change the `category` value in [wizard_state.json](./state/wizard_state.json). The system is designed to create cards dynamically to fit all categories.

Please note that each item **NEEDS** to have a category or else it will not be shown on the "Edit Data" page.

## Changing "Edit Page" Category Order

To change the order of categories displayed on the "Edit Page" navigate to the [edit_page.py](./gui/edit_page.py) and edit the following code:
```
# --- Desired order of categories. Above items are shown first ---
category_order = [
    "Land Use",
    "Crop Production",
    "Greenhouse Farming",
    "Livestock",
    "Revenue, Market Value, and Direct Sales",
    "Workforce",
    "Sustainability",
    "Types of Farms",
    "Other",
]
```

## Adding Another Field

Additional fields should be added to `items` within [wizard_state.json](./state/wizard_state.json).

The important fields are:
<br>`ratio` → Required to extrapolate the data to Southeast Alberta. Percentages need to be in decimal form.
<br> Ex: 0.1 equates to 10%

`file_keyword` → Keyword to find file within /data folder.
<br>Ex: "cattle" to for cattle_inventory.csv

`name_keywords` → List of keywords to filter the name column.
<br>Ex: ["total", "farmland"]

`unit_of_measure` → Needs to be the **exact** same string as is found in the "Unit of measure" column (Or UOM column if "Unit of measure" not found)
<br> Ex: "Acres"

Full formatting is detailed in [Item Schema](#items-schema).

## Adding/Removing a Statistics Canada Agriculture Census Table

The first step should be finding which table to download. One of the easiest ways to check this is by opening up the agriculture_census_tables_20xx.csv files that are downloaded with each import under their respective folder found within /data.

To change which Census of Agriculture tables are downloaded, locate the `extract_census_data()` function found inside of [/scripts/extract_census_data](./scripts/extract_census_data.py).

From there you should find a section that looks like such:
```
# --- Census of Agriculture Tables to be Downloaded ---
# Structure: "file_name": "keywords used to find file"
    download_plan = {
        # Farm classifications
        "farm_type": "farm type",
        "total_farm_area": "total farm area",
        "land_tenure": "land tenure",
        ...
    }
```

The format that this dictionary uses is as follows:
<br>**"file_name": "keywords used to find file"**

The keywords are used to filter through the `cubeTitleEn` column within the agriculture_census_tables_20xx.csv file we looked at earlier.
<br>Keywords can in any order so "used file keywords to find" would work the same.

For example if you wanted information from the "Operating Revenues" table, it might look like:
```
"operating_expenses": "operating expenses"
```

On the next import the system would download operating_expenses.csv.

## Adding Other Statistics Canada Tables
Currently only Agriculture Census tables work with this program. Future table support is outlined in [Future Plans](#future-plans).

# Future Plans

TODO: MAKE SURE DEFAULT WIZARD STATE ACTUALLY IS WORKING

TODO: WHAT IS LEFT:
- ## Priority:
    - REMOVE ONE OF THE TOTAL NUMBER OF FARMS
    - Export data
    - Remove excess pages
    - Documentation:
        - Finish README
            - What is likely to break
            - How to fix
            - How to add/remove anything
            - CENSUS TIMING
        - Complete report documenting what, why, and how I did the thing
- ## Would be nice:
    - Checkboxes for each data value so the user can choose to not export certain values
    - Colour coding for date and status
    - Single executable
    - Ensure libraries used are locked
    - Data entry for the rest of the things
    - Better name for system
    - Fix progress bar in extrapolation step
- ## No time before Sept 5th:
    - Move data into a more permanent database
    - Update all code comments to follow the same formatting
    - Include more than just the census data


TODO: Census timing for maintenance

## Questions

- When finding a new extrapolation ratio is possible should the system:
    1. Overide the previous ratio
    2. Create a new ratio that is an average of all ratios gathered
    3. Ignore the data as if the numbers are there to pull a ratio from there is no need to extrapolate

## Notes to remember
1. There are many different fields that this software does not grab despite available data. The reasoning for this is due to a number of factors:
    <br>A. Data is limited or missing
    <br>B. Provincial data is provided but not enough data to limit/extrapolate to just SE Alberta
    <br>C. The original report did not include the data and to keep the project within scope only the prior data has been continued where possible
Some of these fields may include things such as faba beans, hemp, greenhouse herbs, just to name a few.

## What can be improved
1. Files and their associated keywords should be moved into a singular area. They are meant to be human readable but if this project was to used in another report it would require a significant amount of manual data entry in multiple areas. I am confident there is a change that would only require a "master list" to be input and for the system to dynamically create all of the files and attach the correlated data to the wizard_state.

2. Better logs. Keeping track of what and when something goes wrong will likely be very important in keeping this software working into the future.
The good news is that this system already pushes most activity to a status_label. Creating a method to append each message to a log file, and then calling said method at each instance of status_label is likely the easiest implementation.

3. Moving data to a database. The current system used a needlessly complicated json file which could be streamlined into a 

## Current Directions for End of Week:
- Detail how to add items
- Detail where more data might be found
- Detail issues regarding where data was found

# License

This project is licensed under the [MIT License](./LICENSE).