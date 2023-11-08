import pandas as pd
from helpers import get_list_of_genres


def drop_duplicates(movies_df, movie_name_column, year_column, show=False):
    ''' Function for dropping duplicates of the index (movie_name year) in the movies_df DataFrame

    Parameters
    ----------
    movies_df: pandas.DataFrame
        DataFrame containing the movies
    
    movie_name_column: str
        The name of the column in movies_df that contains the movie names
    
    year_column: str
        The name of the column in movies_df that contains the movie years

    show: bool
        Whether to print the number of duplicates or not

    Returns
    -------
    movies_df: pandas.DataFrame
        The movies_df DataFrame without the duplicates
    '''
    movies_df['id'] = movies_df[movie_name_column] + movies_df[year_column]
    non_unique_index_special = movies_df[movies_df.duplicated(subset=['id'], keep=False)]['id'].tolist()
    movies_df = movies_df[~movies_df['id'].isin(non_unique_index_special)]
    if show:
        print('Number of duplicates: ', len(non_unique_index_special))
    return movies_df.drop(columns=['id'])


def preprocess_movie_metadata(movie_metadata_df,drop_empty_genre=False):
    ''' Function for preprocess of the moie metadata

    We preprocess the data from the movie.metadata.tsv file. we first transform the release_date into a year_release column in string format
    Then, we create an index column that is the concatenation of the name and the year_release. We then drop the duplicates according to this index, 
    because we need this index to be unique in orfer to add the imdb ratings(there is only 235 duplicates). Finaly we transform genres, language anf counties into list
    and we  drop the colums that we don't need.
    
    Parameters
    ----------
    movie_metadata_df: pandas.DataFrame
        DataFrame containing the movies metadata

    drop_empty_genre: bool (to drop the movies without genres)

    Returns
    -------
     movie_metadata_df_preprocess: pandas.DataFrame
        The movies_df DataFrame preprocess acording to our needs
    '''

    
    
    # Transform relase_date into a year_release column in string format
    movie_metadata_df_preprocess = movie_metadata_df.dropna(subset=['release_date']).copy()
    movie_metadata_df_preprocess.loc[:, 'release_date'] = pd.to_datetime(movie_metadata_df_preprocess['release_date'], errors='coerce')
    movie_metadata_df_preprocess.loc[:, 'name'] = movie_metadata_df_preprocess['name'].str.lower()
    movie_metadata_df_preprocess.loc[:,'release_year'] = movie_metadata_df_preprocess['release_date'].dt.year.astype("Int16").astype(str)

    ### clean the data according to the genres column if drop_empty_genre is true
    if drop_empty_genre:
        non_empty_genres = movie_metadata_df_preprocess['genres'].apply(lambda x: False if x == '{}' else True)
        movie_metadata_df_preprocess = movie_metadata_df_preprocess[non_empty_genres]

    ### we will merge with the imdb rating data, to do so we will use the id (name_year) as a key, we then need to drop the duplicates for this index
    movie_metadata_df_preprocess = drop_duplicates(movie_metadata_df_preprocess, 'name', 'release_year')

    #transform the genres, language and countries columns into list
    movie_metadata_df_preprocess['genres'] = movie_metadata_df_preprocess['genres'].apply(get_list_of_genres)
    movie_metadata_df_preprocess['languages'] = movie_metadata_df_preprocess['languages'].apply(get_list_of_genres)
    movie_metadata_df_preprocess['countries'] = movie_metadata_df_preprocess['countries'].apply(get_list_of_genres)

    
    #drop unused columnss
    movie_metadata_df_preprocess = movie_metadata_df_preprocess.drop(columns=['box_office_revenue'])
    movie_metadata_df_preprocess = movie_metadata_df_preprocess.drop(columns=['release_date'])

    return movie_metadata_df_preprocess


def preprocess_full(path_to_data, drop_empty_genre=False):
    ''' Function doing all the preprocess of the data in order the retrieve the final dataframe

   We first preprocess the data from the movie.metadata.tsv file. then we merge it with the plot_summaries.txt file to keep only the movies with a plot.
   finaly we add the imdb ratings to the dataframe. keeping only the movies with a rating and a number of votes.
    Parameters
    ----------
    path_to_data: str
        The path to the data folder we suppose that the folder contains the following files: movie.metadata.tsv, plot_summaries.txt, titles.tsv, ratings.tsv

    drop_empty_genre: bool (to drop the movies without genres)


    Returns
    -------
     movie_metadata_df_preprocess: pandas.DataFrame
        The movies_df DataFrame preprocess acording to our needs
    '''
    print('Preprocessing movie metadata...', end=' ')
    ######load data movie metadata
    column_names = ['wikipedia_id', 'freebase_id', 'name', 'release_date', 'box_office_revenue', 'runtime', 'languages', 'countries', 'genres']
    movie_df = pd.read_table(path_to_data +'movie.metadata.tsv', names=column_names)
    movie_metadata_df = preprocess_movie_metadata(movie_df,drop_empty_genre)
    print('Done')

    ######### load data plot summaries
    plot_column_names = ['wikipedia_id', 'plot']
    movie_plot_df = pd.read_csv(path_to_data+'plot_summaries.txt', sep="\t", names=plot_column_names)

    # merge the two dataframe according to the wikipedia_id
    movie_metadata_plot_ = movie_metadata_df.merge(movie_plot_df, on='wikipedia_id', how='inner')

    # add the imdb ratings
    movie_metadata_full = append_ratings(movie_metadata_df,path_to_data, 'name', 'release_year', in_place=False)

    # clean the data
    movie_metadata_full = movie_metadata_full.drop(columns=['tconst'])
    movie_metadata_full = movie_metadata_full.dropna(subset=['averageRating','numVotes'])
    movie_metadata_full = movie_metadata_full.rename(columns={ 'averageRating': 'Imdb_rating'})

    return movie_metadata_full


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

    
    titles = titles[titles['titleType'] == 'movie']
    titles = titles[['tconst', 'originalTitle', 'startYear']]

    titles['originalTitle'] = titles['originalTitle'].str.lower()
    movies_df[movie_name_column] = movies_df[movie_name_column].str.lower()

    print('Dropping duplicates...', end=' ')
    titles = drop_duplicates(titles, 'originalTitle', 'startYear')
    print('Done')

    print('Merging movies with IMDb titles and ratings...', end=' ')
    movies_merged = pd.merge(movies_df, titles, left_on=[movie_name_column, year_column], right_on=['originalTitle', 'startYear'], how='left')
    movies_merged = movies_merged.drop(columns=['originalTitle', 'startYear'])
    movies_merged = pd.merge(movies_merged, ratings, on='tconst', how='left')
    print('Done')
    
    return movies_merged.reset_index(drop=True)
