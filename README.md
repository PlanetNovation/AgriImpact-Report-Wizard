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

Run the following using your Python executable (modify the python path as necessary):
```
python -m pip install -r requirements.txt
```

This will install all of the required packages.

### 3. Run the Script

After navigating to the root folder run:
```
python statscan_agriculture.py
```

# Usage

Here is a breakdown of each page found within the wizard.

## 1. Import Data Page

From this page the user can download all of the most recent Statistics Canada Census of Agriculture tables into the system.
<br>The system will look at the most recent three census dates and if no tables are found within the past 15 years nothing will be downloaded.

Statistics Canada has historically released the Agriculture Census data in May of the following year. This system will be most effective when run past this time frame. For example 2026 data will likely be released sometime in May 2027.

⚠️ In the event of a timeout it likely means that Statistics Canada is unavailable. Please refer to [Statistics Canada](https://www.statcan.gc.ca/en/start) for potential status issues.

## 2. Extrapolate Data Page

From here the user should extrapolate the data that was just imported into the system. If this page is skipped the newly downloaded data will not be displayed to the user and will not be included in the final export.

## 3. Edit Data Page

Currently this pages primary function is to display the data to the user. Future iterations will allow the user more agency regarding which data is included in the final export.

The user can click on any category card to view a dropdown of data. Clicking on a new card will collapse open cards for convenience.

Within each category card the following information can be found:
- `Name` → The title of each data field.
- `Value` → The associated value. An information bubble can be found that when hovered over will display what units the value is recorded in.
- `Date Saved` → The date the data was saved into the system.
- `Quality` → The status quality Statistics Canada provides for all of its data.
    - "A" → Excellent quality.
    - "B" → Very good quality.
    - "C" → Good quality.
    - "D" → Acceptable quality.
    - "E" → Use with caution.
    - "F" → Too unreliable to be published.

## 4. Export Page

A .csv file will be downloaded to the systems ./exports folder. The current year will be appended to the filename in the format `statscan_wizard_export_20xx.csv`.

⚠️ Files will be overwritten if the system exports within the same year.

# Project Structure

```
project-root/
├── data/                       # CSV imports and intermediate datasets
├── exports/                    # Final processed CSVs
├── gui/                        # GUI scripts
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

While this section can not cover every possible weakness, it can hopefully provide some help in the right direction.

## Statistics Canada Changes Agriculture Census Format

In the event Statistics Canada changes how the Agriculture Census is formatted there a few things that may be able to fix the system depending on the severity of the changes.

### Most Recent Agriculture Census Data Is Not Being Imported

Firstly check to see if the data has been released yet. Data is typically set to release in May of the following year of the census. Refer to the [usage](#1-import-data-page) for more information.

If the data has been released and the system is still not gathering anything then there are two likely occurrences:
1. Statistics Canada has changed the formatting of their data.
2. Statistics Canada has changed the table names.

In the event that the formatting has changed there is likely not much this system can do depending on the severity of the changed.
<br>If the census data is changed to be presented in a complete pdf file, Like the 2016 Agriculture Census was, then there is not much short of a new system that will help with that.

In the event it is simply a table name change the keyword filters for tables can be found in ./scripts/get_census_tables.py in this section:
```
# Keywords to filter for just the Agriculture Census tables
for year in census_years_to_try:
    mask = (
        df['cubeTitleEn'].str.contains("Agriculture", case=False, na=False) &
        df['cubeTitleEn'].str.contains("Census", case=False, na=False) &
        df['cubeTitleEn'].str.contains(str(year), case=False, na=False)
    )
    filtered = df[mask]
```

### Specific Data Is No Longer Being Imported

Firstly check to see if the table exists within the ./data folder under agriculture_census_tables_20xx.csv. Cross-referencing the tabes present within the folders between years will likely be helpful in pinpointing if and/or which tables are missing.

It is likely the same issues as the previous section:
1. The table does not exist.
2. The table name has been altered/changed.
3. The table exists however table formatting has changed

If the table does not exist within the agriculture_census_tables_20xx.csv folder then refer to the previous section to see potential issues regarding finding tables.

If the table does exist within agriculture_census_tables_20xx.csv but under a different name than previous years then refer to [this guide](#addingremoving-a-statistics-canada-agriculture-census-table) on how to add/remove tables.
<br> It may be as simple as changing "bees" to "beekeepers".

If it is a change of how the tables are formatted there are too many possibilities to cover within this documentation. Good Luck!

# Extending the System (How to add, change, or remove fields/features)

Many of these customization options are planned to be moved to a more permanent solution. Information can be found in [Future Plans](#future-plans).

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
TODO: WHAT IS LEFT:
- ## Priority:
    - Documentation:
        - Remove excess content from README.md
        - Complete report documenting what, why, and how I did the thing
    - Ensure tge default wizard state functions as intended
- ## Would be nice:
    - Checkboxes for each data value so the user can choose to not export certain values
    - Colour coding for date and status
    - Single executable
    - Ensure libraries used are locked
    - Data entry for the rest of the things
    - Better name for system
    - Fix progress bar in extrapolation step
    - Document #future-plans better
- ## No time before Sept 5th:
    - Move data into a more permanent database
    - Update all code comments to follow the same formatting
    - Include more than just the census data

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