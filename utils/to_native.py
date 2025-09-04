def to_native(value):
    """Convert numpy/pandas types to native Python types."""
    if hasattr(value, "item"):  # works for np.int64, np.float64, pd.Series scalars
        return value.item()
    return value