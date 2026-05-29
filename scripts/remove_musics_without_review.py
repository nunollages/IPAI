import pandas as pd
import re
import ast
import unicodedata

songs_df = pd.read_csv("data/songs.csv")
reviews_df = pd.read_csv("data/pitchfork_reviews.csv", sep=";")

# Remover espaços no final
songs_df.columns = songs_df.columns.str.strip()
reviews_df.columns = reviews_df.columns.str.strip()

# Normaliza o texto para facilitar comparações
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()

    # Remover acentos
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    text = text.replace("&", " and ")

    # Remover pontuação
    text = re.sub(r"[^\w\s]", " ", text)

    # Remover espaços repetidos
    text = re.sub(r"\s+", " ", text).strip()

    return text

# Converte uma lista de String de Artistas em uma lista Python
def parse_artists(value):
    if isinstance(value, list):
        return value
    if pd.isna(value):
        return []
    value = str(value).strip()
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return [value]

songs_album_col = "album_name"
songs_artists_col = "artists"

reviews_album_col = "album"
reviews_artist_col = "artist"

reviews_df["album_norm"] = reviews_df[reviews_album_col].apply(normalize_text)
reviews_df["artist_norm"] = reviews_df[reviews_artist_col].apply(normalize_text)

reviews_match = (
    reviews_df[["album_norm", "artist_norm"]]
    .dropna()
    .drop_duplicates()
)

songs_df["album_norm"] = songs_df[songs_album_col].apply(normalize_text)
songs_df[songs_artists_col] = songs_df[songs_artists_col].apply(parse_artists)

# Para cada musica guarda uma entrada para cada artista pertencente à mesma
songs_exploded = songs_df.explode(songs_artists_col).copy()
songs_exploded["artist_norm"] = songs_exploded[songs_artists_col].apply(normalize_text)

songs_exploded = songs_exploded[
    (songs_exploded["album_norm"] != "") & (songs_exploded["artist_norm"] != "")
].copy()

reviews_match = reviews_match[
    (reviews_match["album_norm"] != "") & (reviews_match["artist_norm"] != "")
].copy()

# Merge entre as músicas e as reviews
matched = songs_exploded.merge(
    reviews_match,
    on=["album_norm", "artist_norm"],
    how="inner"
)

print("Linhas matched:", len(matched))

# Remove duplicados gerados pelo exploded
songs_filtered = matched.drop_duplicates(subset=songs_df.columns.tolist()).copy()

songs_filtered = songs_filtered.drop(columns=["album_norm", "artist_norm"], errors="ignore")

print(songs_filtered.head())
print("Total músicas filtradas:", len(songs_filtered))

songs_filtered.to_csv("data/songs_with_reviewed_albums.csv", index=False)