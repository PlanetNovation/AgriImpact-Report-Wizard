import pandas as pd

def get_product_id_by_keyword(file_path, keyword, col="cubeTitleEn"):
    """
    Returns the productId (int) for the first row where the specified column 
    contains the given keyword.

    Args:
        file_path (str): Path to the CSV file.
        keyword (str): The search keyword.
        col (str): The column to search in (default = "cubeTitleEn").

    Returns:
        int or None: The productId if found, otherwise None.
    """
    df = pd.read_csv(file_path)
    
    match = df[df[col].str.contains(keyword, case=False, na=False)]

    if not match.empty:
        return int(match.iloc[0]["productId"])
    return None
