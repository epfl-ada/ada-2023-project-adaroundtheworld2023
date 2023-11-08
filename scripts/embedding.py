import os
import re

import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer


def get_embedding(text: str, model) -> np.ndarray:
    """
    Split texts into sentences and get embeddings for each sentence.
    The final embeddings is the mean of all sentence embeddings.
    reference: https://towardsdatascience.com/easily-get-high-quality-embeddings-with-sentencetransformers-c61c0169864b

    :param text: Input text.
    :param model: update. For embedding.
    :return: Embeddings.
    """
    return np.mean(
        model.encode(
            list(set(re.findall('[^!?。.？！]+[!?。.？！]?', text)))
        ), axis=0)


if __name__ == '__main__':
    column_names = [
        'wikipedia_id', 'freebase_id', 'name', 'release_date', 'box_office_revenue',
        'runtime', 'languages', 'countries', 'genres'
    ]
    movie_metadata_df = pd.read_table('../data/raw/movie.metadata.tsv', names=column_names)

    plot_column_names = ['wikipedia_id', 'plot']
    plot_df = pd.read_csv('../data/raw/plot_summaries.txt', sep="\t", names=plot_column_names)

    merged_df = movie_metadata_df[['wikipedia_id', 'name']].merge(plot_df, on='wikipedia_id', how='inner')

    model = SentenceTransformer('../model/e5-large-v2')
    input_template = 'query: {}'
    text = 'test 123'
    embeddings = model.encode(input_template.format(text), normalize_embeddings=True)

    kala = 1