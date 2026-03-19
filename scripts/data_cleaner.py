import pandas as pd
import ast


SONGS = "data/songs.csv"
ARTISTS = "data/artists.csv"
REVIEWS = "data/pitchfork_reviews.csv"

songs_df = pd.read_csv(SONGS, sep=',')
artists_df = pd.read_csv(ARTISTS, sep=',')
reviews_df = pd.read_csv(REVIEWS, sep=';')

# Songs dataset cleaning
songs_df.info()
songs_df = songs_df.dropna(subset=['album_name'])
songs_df = songs_df[~(songs_df['lyrics'].str.contains(r'\[Instrumental\]', na=False))]

# Artists dataset cleaning 
artists_df.info()
artists_df = artists_df.dropna()

# Reviews dataset cleaning 
reviews_df.info()
reviews_df = reviews_df.dropna()
reviews_df = reviews_df.drop_duplicates()
# Convert the list of genres into a real list
artists_df['genres'] = artists_df['genres'].apply(ast.literal_eval)

# Normalizar nomes
songs_df['album_name'] = songs_df['album_name'].str.lower().str.strip()
reviews_df['album'] = reviews_df['album'].str.lower().str.strip()

songs_df['artists'] = songs_df['artists'].str.lower().str.strip()
reviews_df['artist'] = reviews_df['artist'].str.lower().str.strip()
artists_df['name'] = artists_df['name'].str.lower().str.strip()

songs_df['genre'] = songs_df['genre'].str.lower().str.strip()
reviews_df['genre'] = reviews_df['genre'].str.lower().str.strip()
artists_df['main_genre'] = artists_df['main_genre'].str.lower().str.strip()
artists_df['genres'] = artists_df['genres'].apply(
    lambda x: [g.lower().strip() for g in x]
)


# Kepp only reviews of the existing albums (9012 Reviews)
albums = songs_df['album_name'].dropna().unique()
reviews_df = reviews_df[reviews_df['album'].isin(albums)]


# Export the cleaned data to a csv file
"""
songs_df.to_csv("data/clean_songs.csv", index=False)
artists_df.to_csv("data/clean_artists.csv", index=False)
reviews_df.to_csv("data/clean_reviews.csv", index=False)
"""
