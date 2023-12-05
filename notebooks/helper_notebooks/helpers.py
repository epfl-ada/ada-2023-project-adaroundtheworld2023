"""helpers.py: helper functions for notebooks"""
import json
import os
import re
from pathlib import Path

import numpy as np


def get_list_from_string_dict(value: str) -> list:
    """Parse dict string and return the list of strings with genres."""
    return list(json.loads(value).values())


def get_embedding(text: str, model) -> np.ndarray:
    """
    Split texts into sentences and get embeddings for each sentence.
    The final embeddings is the mean of all sentence embeddings.
    Reference: https://towardsdatascience.com/easily-get-high-quality-embeddings-with-sentencetransformers-c61c0169864b

    :param text: Input text.
    :param model: update. For embedding.
    :return: Embeddings.
    """
    input_template = 'query: {}'
    phrases = list(set(re.findall('[^!?。.？！]+[!?。.？！]?', text)))
    phrases_formatted = [input_template.format(phrase) for phrase in phrases]
    return np.mean(model.encode(phrases_formatted, normalize_embeddings=True), axis=0)


def get_embeddings_from_json(year: int) -> dict:
    """
    Return the dictionary with all embeddings (as numpy arrays) for the decade.
        Decades could be from 1900 to 2010.

    :param year: start of the decade
    :return: dict with key as movie ID and value as embedding.
    """
    root_path = Path(__file__).parent.parent
    filepath = os.path.join(root_path, 'data', 'embeddings', 'plots',  f'plots_{year}s.json')

    # read the file
    with open(filepath, 'r') as f:
        data = json.load(f)

    # convert all lists to vectors and string keys to int
    return {int(key): np.array(value) for key, value in data.items()}


def get_similarities_from_json(year: int) -> dict:
    """
    Return the dictionary with all the similarities between the movies for the decade.
        Decades could be from 1900 to 2010.

    :param year: start of the decade
    :return: dict with key as tuple of (id_movie_1, id_movie_2): similarity score
    """
    root_path = Path(__file__).parent.parent
    filepath = os.path.join(root_path, 'data', 'embeddings', 'similarities', f'similarities_{year}s.json')

    # read the file
    with open(filepath, 'r') as f:
        data = json.load(f)

    # convert string key to tuple of integers
    return {tuple([int(movie) for movie in key.split('-')]): value for key, value in data.items()}
