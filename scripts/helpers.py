"""helpers.py: helper functions for notebooks"""
import json
import re

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



