import numpy as np

def convert_and_clip_data(data, data_type_selection):
    """
    Converts the NumPy array 'data' to the selected data type and clips values to fit the new type's range.

    :param data: The NumPy array to be converted.
    :param data_type_selection: A string representing the selected data type.
    :return: Converted NumPy array.
    """
    data_type_ranges = {
        "int8": (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
        "uint8": (np.iinfo(np.uint8).min, np.iinfo(np.uint8).max),
        "int16": (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
        "uint16": (np.iinfo(np.uint16).min, np.iinfo(np.uint16).max),
        "int32": (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
        "uint32": (np.iinfo(np.uint32).min, np.iinfo(np.uint32).max),
        "int64": (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
        "uint64": (np.iinfo(np.uint64).min, np.iinfo(np.uint64).max),
        "float": (np.finfo(np.float32).min, np.finfo(np.float32).max),
        "double": (np.finfo(np.float64).min, np.finfo(np.float64).max)
    }

    if data_type_selection in data_type_ranges:
        min_val, max_val = data_type_ranges[data_type_selection]
        # Clip values to the range of the new data type
        clipped_data = np.clip(data, min_val, max_val)
        # Convert data type
        converted_data = clipped_data.astype(getattr(np, data_type_selection))
        return converted_data
    else:
        raise ValueError("Invalid data type selection.")