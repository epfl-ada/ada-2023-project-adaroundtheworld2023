import json


def get_list_of_genres(value: str) -> list:
    """Parse dict string and return the list of strings with genres."""
    return list(json.loads(value).values())


def get_str_of_genres(value: str) -> str:
    """Parse dict string and return only genres as joint lower-case string separated by ','."""
    return ','.join(get_list_of_genres(value)).lower()
