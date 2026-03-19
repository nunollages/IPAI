import pandas as pd
import requests
import time
import re
from typing import Optional, Dict, List
import json

INPUT_CSV = "data/songs.csv"
OUTPUT_CSV = "songs_with_release_date_api.csv"

TRACK_COL = "name"
ARTIST_COL = "artists"
MAIN_ARTIST_COL = "main_artist"


BASE_URL = "https://musicbrainz.org/ws/2/recording"
HEADERS = {
    "User-Agent": "IPAI-Project/1.0 (Group5_IPAI@fcul.pt)"
}

songs_db = pd.read_csv('data/songs.csv')

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

def search_musicbrainz_recording(track_name: str, artist_name: str, limit: int = 10) -> List[Dict]:
    params = {
        "query": f'recording:"{track_name}" AND artist:"{artist_name}"',
        "fmt": "json",
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json().get("recordings", [])

def get_release_date(track_name: str, artist_name: str) -> Optional[str]:
    try:
        recordings = search_musicbrainz_recording(track_name, artist_name)
    except requests.RequestException:
        return None

    candidates = []

    for recording in recordings:
        rec_title = normalize_text(recording.get("title"))

        for release in recording.get("releases", []):
            release_date = release.get("date")
            if not release_date:
                continue

            score = 0

            # Prefer best music track name matches
            if rec_title == normalize_text(track_name):
                score += 2
            elif normalize_text(track_name) in rec_title or rec_title in normalize_text(track_name):
                score += 1

            # Prefer complete dates
            if len(release_date) == 10:
                score += 3
            elif len(release_date) == 7:
                score += 2
            elif len(release_date) == 4:
                score += 1

            candidates.append((score, release_date))

    if not candidates:
        return None

    candidates.sort(key=lambda x: (-x[0], x[1]))
    return candidates[0][1]

# Create a new column only with the main artist
songs_db[MAIN_ARTIST_COL] = songs_db[ARTIST_COL].apply(extract_main_artist)

songs_db["name_norm"] = songs_db[TRACK_COL].apply(normalize_text)
songs_db["artist_norm"] = songs_db[MAIN_ARTIST_COL].apply(normalize_text)

unique_pairs = (
    songs_db[["name", "main_artist", "name_norm", "artist_norm", "popularity"]]
    .dropna(subset=["name_norm", "artist_norm"])
    .sort_values("popularity", ascending=False)
    .drop_duplicates(subset=["name_norm", "artist_norm"])
    .head(10000)
    .reset_index(drop=True)
)

print(len(unique_pairs))
print(unique_pairs.head())

results = []

for idx, row in unique_pairs.iterrows():
    track_name = str(row[TRACK_COL])
    artist_name = str(row[MAIN_ARTIST_COL])

    release_date = get_release_date(track_name, artist_name)

    results.append({
        TRACK_COL: track_name,
        MAIN_ARTIST_COL: artist_name,
        "release_date": release_date
    })

    print(f"[{idx + 1}/{len(unique_pairs)}] {track_name} - {artist_name} -> {release_date}")
    time.sleep(1.1)

results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"\nNovo CSV criado: {OUTPUT_CSV}")