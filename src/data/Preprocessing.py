import pandas as pd
import ast
import pickle
"""
TMDB Movie Dataset v11: Columns
id  title  vote_average  vote_count  status  release_date  revenue  runtime  adult  backdrop_path
budget  homepage  overview  poster_path  tagline  genres  production_companies  spoken_languages
keywords

>> title | vote_average | vote_count | release_date | overview | genres | production_companies | keywords
"""
df = pd.read_csv('TMDB_movie_dataset_v11.csv')
df = df[['title', 'genres', 'keywords', 'overview', 'vote_average', 'vote_count', 'release_date', 'production_companies']]
# print(df['genres'].head())
print(f"Before dropna: {df.shape[0]} movies exist.")
df.dropna(inplace=True)

def parse_list(col):
    if pd.isnull(col):
        return []
    return [x.strip() for x in col.split(',')]

df['genres'] = df['genres'].apply(parse_list)
df['keywords'] = df['keywords'].apply(parse_list)
df['production_companies'] = df['production_companies'].apply(parse_list)
df['vote_average'] = df['vote_average'].round(1)

# print(df['genres'].head())

df.to_pickle('TMDB_movie_dataset.pkl')

# pickle test
test = pd.read_pickle('TMDB_movie_dataset.pkl')
print(test[['title', 'vote_average']])