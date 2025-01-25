import math
import pandas as pd
import pickle
import time
import functools
import random
from collections import Counter, OrderedDict
import logging

# ------------------------------------------------------------------------------
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Utility Decorators

def timer(func):
    """Decorator to measure execution time of a function."""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f"Duration {run_time:.2f} secs: {func.__doc__}")
        return value
    return wrapper_timer

# ------------------------------------------------------------------------------
# Predicates

def is_element_filled(element, dictionary):
    """Checks if an element exists in a dictionary and is not None."""
    return element in dictionary and dictionary[element] is not None

def has_unique_index(dataframe):
    """Checks if a pandas DataFrame has unique index values."""
    return not dataframe.duplicated(keep="first").any()

# ------------------------------------------------------------------------------
# Serialization

@timer 
def serialize_object(obj, filename):
    """Serializes an object to a file using pickle."""
    with open(filename, "wb") as file:
        pickle.dump(obj, file)

@timer 
def deserialize_object(filename):
    """Deserializes an object from a pickle file."""
    with open(filename, "rb") as file:
        return pickle.load(file)

# ------------------------------------------------------------------------------
# Data Cleaning and Processing

def extract_column_base_features(column, pattern):
    """Extracts base features from a string column by splitting on a given pattern."""
    return [x[0] for x in column.str.split(pat=pattern)]

def determine_dynamic_column_order(column_values, fixed_columns, metadata):
    """Determines a dynamic column order by removing predefined metadata fields."""
    columns = list(column_values)
    removable_columns = [
        "Index", "ID", metadata["meta_typ"], metadata["meta_description"],
        "Wertebereich", "F_Aktiv", "F_PCA", "F_Szen"
    ]
    columns = [col for col in columns if col not in removable_columns]
    return fixed_columns + columns

def cleanse_column_names(columns, characters):
    """Removes specified characters from column names."""
    for char in characters:
        columns = columns.str.replace(char, '', regex=True)
    return columns

def remove_nan_from_list(lst):
    """Removes NaN values from a list."""
    return [i for i in lst if str(i) != "nan"]

def remove_none_from_list(lst):
    """Removes None values from a list."""
    return [i for i in lst if i is not None]

def remove_nan_from_dict(dictionary):
    """Removes key-value pairs with NaN values from a dictionary."""
    return {k: v for k, v in dictionary.items() if str(v) != "nan"}

def remove_none_from_dict(dictionary):
    """Removes key-value pairs with None values from a dictionary."""
    return {k: v for k, v in dictionary.items() if v is not None}

# ------------------------------------------------------------------------------
# Math Operations

def intersection(set1, set2):
    """Returns the intersection of two sets."""
    return list(set(set1).intersection(set2))

def binomial_coefficient(n, k):
    """Computes the binomial coefficient (n choose k)."""
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate_random_color():
    """Generates a random hexadecimal color code."""
    return "#" + "".join(random.choice('0123456789ABCDEF') for _ in range(6))

def count_frequencies(iterable):
    """Counts frequency of elements in an iterable and returns an ordered dictionary."""
    return OrderedDict(sorted(Counter(iterable).items()))

# ------------------------------------------------------------------------------
# DataFrame Operations

def pop_row_from_dataframe(df, index_value):
    """Removes a row from a DataFrame and returns the row as a list and the modified DataFrame."""
    popped_row = df.loc[index_value, :].tolist()
    shrunk_df = df.drop(index_value)
    return popped_row, shrunk_df

@timer
def sort_dataframe(df, column, ascending=True):
    """Sorts a DataFrame based on a specific column."""
    sorted_df = pd.DataFrame(columns=df.columns)
    while not df.empty:
        min_or_max_value = df[column].min() if ascending else df[column].max()
        index_values = df.index[df[column] == min_or_max_value].tolist()
        popped_row, df = pop_row_from_dataframe(df, index_values[0])
        sorted_df = pd.concat([sorted_df, pd.DataFrame([dict(zip(df.columns, popped_row))])], ignore_index=True)
    return sorted_df

def assign_column_aliases(df, alias_mapping):
    """Renames DataFrame columns based on an alias mapping dictionary."""
    return df.rename(columns=dict(zip(alias_mapping["scenario"], alias_mapping["sc_alias"])))

def check_data_quality(df, required_columns, column_formats, value_ranges=None):
    """Automatically checks the data quality of a DataFrame."""
    issues = {}

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues['missing_columns'] = missing_columns

    format_issues = {
        col: f"Expected {expected_type}, found different types"
        for col, expected_type in column_formats.items()
        if col in df.columns and not df[col].map(lambda x: isinstance(x, expected_type)).all()
    }
    if format_issues:
        issues['format_issues'] = format_issues

    missing_values = df.isnull().sum()
    if missing_values.any():
        issues['missing_values'] = missing_values[missing_values > 0].to_dict()

    if value_ranges:
        range_issues = {
            col: f"Values out of range [{min_val}, {max_val}]"
            for col, (min_val, max_val) in value_ranges.items()
            if col in df.columns and df[(df[col] < min_val) | (df[col] > max_val)].any().any()
        }
        if range_issues:
            issues['range_issues'] = range_issues

    if df.duplicated().any():
        issues['duplicates'] = f"Found {df.duplicated().sum()} duplicate rows"

    return issues
