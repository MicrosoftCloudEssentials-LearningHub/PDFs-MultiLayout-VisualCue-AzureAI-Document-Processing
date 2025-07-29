"""
Data Helper Functions
Utilities for data manipulation and processing
"""

import logging


def safe_get_nested_value(dictionary, keys, default=None):
    """Safely get nested dictionary value using dot notation keys"""
    try:
        value = dictionary
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def truncate_text(text, max_length=100, suffix="..."):
    """Truncate text to specified length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
