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



