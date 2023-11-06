import pandas as pd

def append_ratings(movies_df, data_root, movie_name_column, year_column, in_place=False):
    ''' Function for adding the IMDb ratings to the movies_df DataFrame

    We add the ratings by matching the movie names and years in the movies_df DataFrame to the
    corresponding entries in the IMDb titles.tsv file. Then we will add the ratings to the
    merged_df based on tconst column, containing the IMDb ID for each title.

    Parameters
    ----------
    movies_df: pandas.DataFrame
        DataFrame containing the movies
        Assumption: The dataframe must have a name column and a year column, and the (name, year)
        pairs must be unique
    data_root: str
        The path to the data folder
        Assumption: The folder must contain the following files (With the respective name):
            - titles.tsv ([name.basics.tsv.gz](https://datasets.imdbws.com/title.basics.tsv.gz))
            - ratings.tsv ([title.ratings.tsv.gz](https://datasets.imdbws.com/title.ratings.tsv.gz))
    movie_name_column: str
        The name of the column in movies_df that contains the movie names
        Assumption: The column must be of type str
    year_column: str
        The name of the column in movies_df that contains the movie years
        Assumption: The column must be of type str and contain only the year (ex: 2001)
    in_place: bool
        Whether to modify the movies_df in place or return a new DataFrame

    Returns
    -------
    movies_df: pandas.DataFrame
        The movies_df DataFrame with the ratings added
    '''

    if not in_place:
        movies_df = movies_df.copy()
    
    print('Reading titles.tsv...', end=' ')
    titles = pd.read_csv(data_root + 'titles.tsv', sep='\t', low_memory=False)
    print('Done')

    assert ('tconst' in titles.columns), 'The titles.tsv file must contain the tconst column'
    assert ('titleType' in titles.columns), 'The titles.tsv file must contain the titleType column'
    assert ('originalTitle' in titles.columns), 'The titles.tsv file must contain the originalTitle column'

    print('Reading ratings.tsv...', end=' ')
    ratings = pd.read_csv(data_root + 'ratings.tsv', sep='\t')
    print('Done')

    assert ('tconst' in ratings.columns), 'The ratings.tsv file must contain the tconst column'
    assert ('numVotes' in ratings.columns), 'The ratings.tsv file must contain the numVotes column'
    assert ('averageRating' in ratings.columns), 'The ratings.tsv file must contain the averageRating column'

    print('Merging movies with IMDb titles and ratings...', end=' ')
    titles = titles[titles['titleType'] == 'movie']
    titles = titles[['tconst', 'originalTitle', 'startYear']]

    titles['originalTitle'] = titles['originalTitle'].str.lower()
    movies_df[movie_name_column] = movies_df[movie_name_column].str.lower()

    movies_merged = pd.merge(movies_df, titles, left_on=[movie_name_column, year_column], right_on=['originalTitle', 'startYear'], how='left')
    movies_merged = movies_merged.drop(columns=['originalTitle', 'startYear'])

    movies_merged = pd.merge(movies_merged, ratings, on='tconst', how='left')
    print('Done')
    
    return movies_merged