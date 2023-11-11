"""helpers.py: helper functions for notebooks"""
import json


def get_list_from_string_dict(value: str) -> list:
    """Parse dict string and return the list of strings with genres."""
    return list(json.loads(value).values())


