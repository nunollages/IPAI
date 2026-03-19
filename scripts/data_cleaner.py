import pandas as pd

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

# Export the cleaned data to a csv file
songs_df.to_csv("data/clean_songs.csv", index=False)
artists_df.to_csv("data/clean_artists.csv", index=False)
reviews_df.to_csv("data/clean_reviews.csv", index=False)
