import pandas as pd
import re
from typing import Optional, Dict, List
import json

MUSIC_WITH_DATE = "data/tracks.csv"
MUSIC_WITH_LYRICS = "data/songs.csv"

tracks_df = pd.read_csv(MUSIC_WITH_DATE)
songs_df = pd.read_csv(MUSIC_WITH_LYRICS)

def normalize_text(text: Optional[str]) -> str:
    if text is None:
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

def extract_main_artist(artists_value):
    if pd.isna(artists_value):
        return None

    try:
        artists_list = json.loads(artists_value)
        if isinstance(artists_list, list) and len(artists_list) > 0:
            return artists_list[0].strip()
    except Exception:
        if isinstance(artists_value, str) and "," in artists_value:
            return artists_value.split(",")[0].strip()

    return None

songs_df["main_artist"] = songs_df["artists"].apply(extract_main_artist)
tracks_df["main_artist"] = tracks_df["artists"].apply(extract_main_artist)

def normalize(text):
    if pd.isna(text):
        return None
    return str(text).lower().strip()

songs_df["main_artist"] = songs_df["artists"].apply(extract_main_artist)
tracks_df["main_artist"] = tracks_df["artists"].apply(extract_main_artist)


def normalize(text):
    if pd.isna(text):
        return None
    return str(text).lower().strip()

songs_df["name_norm"] = songs_df["name"].apply(normalize)
songs_df["artist_norm"] = songs_df["main_artist"].apply(normalize)

tracks_df["name_norm"] = tracks_df["name"].apply(normalize)
tracks_df["artist_norm"] = tracks_df["main_artist"].apply(normalize)

merged_df = songs_df.merge(
    tracks_df[["name_norm", "artist_norm", "release_date"]],
    on=["name_norm", "artist_norm"],
    how="left"
)

print(merged_df["release_date"].notna().sum())




