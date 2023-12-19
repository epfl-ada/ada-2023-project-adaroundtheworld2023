"""helpers.py: helper functions for notebooks"""
import itertools
import json
import os
import pickle
import random
import re
from typing import Callable

import numpy as np
import pandas as pd
import networkx as nx
import functools as ft

from pathlib import Path
from bokeh.models import ColumnDataSource, DataTable, TableColumn


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


def get_embeddings_from_json(year: int, approach: str) -> dict:
    """
    Return the dictionary with all embeddings (as numpy arrays) for the decade.
        Decades could be from 1900 to 2010.

    :param year: start of the decade
    :return: dict with key as movie ID and value as embedding.
    """
    root_path = Path(__file__).parent.parent
    filepath = os.path.join(root_path, 'data', 'embeddings', approach,  f'plots_{year}s.json')

    # read the file
    with open(filepath, 'r') as f:
        data = json.load(f)

    # convert all lists to vectors and string keys to int
    return {int(key): np.array(value) for key, value in data.items()}


def get_similarities_from_json(decade: int, approach: str) -> dict:
    """
    TODO: update
    """
    root_path = Path(__file__).parent.parent
    filepath = os.path.join(root_path, 'data', 'similarities', approach, f'similarities_{decade}s.json')

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
    filepath = os.path.join(root_path, 'data', 'classification', 'custom_genres', f'plots_{year}s.json')

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


def get_graph_from_pickle(year: int, approach: str):
    """
    Return the graph object for the decade. Decades could be from 1900 to 2010.

    :param year: start of the decade
    :param approach: either 'embeddings', 'raw_genres' or 'custom_genres'
    :return: networkx graph object
    """
    root_path = Path(__file__).parent.parent
    filepath = os.path.join(root_path, 'data', 'graphs', approach, f'{year}s.gpickle')

    # read the file
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def merge_graph_to_df(
        df: pd.DataFrame,
        graph,
        features: list = ['betweenness', 'degree', 'log_betweenness']
) -> pd.DataFrame:
    """
    Add betweenness and degree to the df and only keep the columns with nodes.

    :param df: with preprocessed data and wikipedia_id as index
    :param graph: networkx object
    :param features: attributes that must be extracted from the graph
    :return: df with (log)betweenness and degree
    """
    dfs = [df]

    for feature in features:
        attribute = nx.get_node_attributes(graph, feature)
        attribute = {int(key): value for key, value in attribute.items()}
        attribute_df = pd.DataFrame.from_dict(attribute, orient='index').rename(columns={0: feature})
        dfs.append(attribute_df)

    return ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True), dfs)

def get_embeddings_from_genres_and_themes(proba: dict) -> dict:
    """
    Merge probabilities of genres and themes and normalize to unit vectors.

    :param proba: dictionary with LLM results as dictionary.
    :return: dictionary with "embeddings"
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


def get_bokeh_table(df: pd.DataFrame):
    """Convert pandas df to Bokeh's DataTable."""
    source = ColumnDataSource(df)

    cols = []
    for col_name in df.columns:
        cols.append(TableColumn(field=col_name, title=col_name))

    return DataTable(source=source, columns=cols)


def add_default_attributes(graph, df: pd.DataFrame):
    """

    :param graph:
    :param df:
    :return:
    """

    def _add_features_from_df(graph, df: pd.DataFrame, features: list):
        """Helper function for adding features from df to graph."""
        graph_df = df.set_index('wikipedia_id')

        for feature in features:
            ratings_dict = dict((id_, graph_df.loc[int(id_)][feature]) for id_ in graph.nodes)
            nx.set_node_attributes(graph, name=feature, values=ratings_dict)

        return graph

    features_from_df = ['name', 'rating', 'release_year']
    graph = _add_features_from_df(graph, df, features_from_df)

    # add wikipedia id itself as an attribute
    names = dict((id_, int(id_)) for id_ in graph.nodes)
    nx.set_node_attributes(graph, name='wikipedia_id', values=names)

    # calculate the betweenness centrality
    betweenness = nx.betweenness_centrality(graph)
    nx.set_node_attributes(graph, name='betweenness', values=betweenness)

    log_betweenness = {key: np.log(value + 0.0001) for key, value in betweenness.items()}
    nx.set_node_attributes(graph, name='log_betweenness', values=log_betweenness)

    # calculate degree for each node
    degrees = dict(nx.degree(graph))
    nx.set_node_attributes(graph, name='degree', values=degrees)

    return graph
