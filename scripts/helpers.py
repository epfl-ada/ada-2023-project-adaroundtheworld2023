"""helpers.py: helper functions for notebooks"""
import itertools
import json
import os
import pickle
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
import functools as ft


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
    mean_vector = np.mean(model.encode(phrases_formatted, normalize_embeddings=True), axis=0)
    norm = np.linalg.norm(mean_vector)
    return mean_vector / norm



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


def get_classification_from_json(year: int) -> dict:
    """
    Return the dictionary with all the classification values of the movies for the decade.
        Decades could be from 1900 to 2010.

    :param year: start of the decade
    :return: dict with key wikipedia_id
    """
    root_path = Path(__file__).parent.parent
    filepath = os.path.join(root_path, 'data', 'classification', 'plots', f'plots_{year}s.json')

    # read the file
    with open(filepath, 'r') as f:
        return json.load(f)


def get_similarity_df(movie_df: pd.DataFrame, similarities: dict, movie_count: int, seed: int = 23):
    movies = list(set(itertools.chain(*similarities.keys())))

    random.seed(seed)
    subsample_movies = random.sample(movies, movie_count)
    subsample_combinations = list(itertools.combinations(subsample_movies, 2))

    similarity_df = pd.DataFrame(columns=['movie_1', 'movie_2', 'similarity'], dtype=float)

    for id_1, id_2 in subsample_combinations:

        if id_1 == id_2:
            similarity_df.loc[len(similarity_df)] = [movie_df.loc[id_1]['name'], movie_df.loc[id_2]['name'], 100]
            continue

        try:
            similarity = similarities[(id_1, id_2)]
        except KeyError:
            similarity = similarities[(id_2, id_1)]

        similarity_df.loc[len(similarity_df)] = [
            movie_df.loc[id_1]['name'], movie_df.loc[id_2]['name'], similarity
        ]

    return similarity_df


def get_graph_from_pickle(year: int):
    """
    Return the graph object for the decade. Decades could be from 1900 to 2010.

    :param year: start of the decade
    :return: networkx graph object
    """
    root_path = Path(__file__).parent.parent
    filepath = os.path.join(root_path, 'data', 'embeddings', 'graphs', f'{year}s.gpickle')

    # read the file
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def merge_graph_to_df(df: pd.DataFrame, graph) -> pd.DataFrame:
    """
    Add betweenness and degree to the df and only keep the columns with nodes.

    :param df: with preprocessed data and wikipedia_id as index
    :param graph: networkx object
    :return: df with betweenness and degree
    """
    betweenness = nx.get_node_attributes(graph, "betweenness")
    betweenness = {int(key): value for key, value in betweenness.items()}
    betweenness_df = pd.DataFrame.from_dict(betweenness, orient='index').rename(columns={0: 'betweenness'})

    degree = nx.get_node_attributes(graph, "degree")
    degree = {int(key): value for key, value in degree.items()}
    degree_df = pd.DataFrame.from_dict(degree, orient='index').rename(columns={0: 'degree'})

    dfs = [df, betweenness_df, degree_df]
    return ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True), dfs)


def get_embeddings_from_proba(proba: dict) -> dict:
    """
    TODO: update
    :param proba:
    :return:
    """
    embedding_dict = {}

    for key in proba.keys():
        x = proba[key]
        _, genres = zip(*sorted(zip(x['genres']['labels'], x['genres']['scores'])))
        _, themes = zip(*sorted(zip(x['themes']['labels'], x['themes']['scores'])))

        embedding = np.array(genres + themes)
        norm_embedding = embedding / np.linalg.norm(embedding)
        embedding_dict[key] = norm_embedding.squeeze()

    return embedding_dict
