import pandas as pd
import ast

songs_date_df = pd.read_csv("data/songs_with_release_date_api.csv")
songs_df = pd.read_csv("data/songs_with_reviewed_albums.csv")

songs_df = songs_df.drop("year", axis=1)

# 🧠 Guardar nome original
songs_date_df["name_original"] = songs_date_df["name"]

# Normalizar
songs_date_df["name"] = songs_date_df["name"].str.lower().str.strip()
songs_date_df["main_artist"] = songs_date_df["main_artist"].str.lower().str.strip()

songs_df["name"] = songs_df["name"].str.lower().str.strip()

# Limpar artistas
def clean_artist(x):
    if pd.isna(x):
        return None
    
    try:
        parsed = ast.literal_eval(x)
        if isinstance(parsed, list):
            return parsed[0]
        return parsed
    except:
        return x  

songs_df["artist_clean"] = songs_df["artists"].apply(clean_artist)
songs_df["artist_clean"] = songs_df["artist_clean"].str.lower().str.strip()

# Merge
merged_df = pd.merge(
    songs_date_df,
    songs_df,
    left_on=["name", "main_artist"],
    right_on=["name", "artist_clean"],
    how="inner"
)

# 🔄 Restaurar nome original
merged_df["name"] = merged_df["name_original"]

# 🧹 Remover colunas que já não queres
merged_df = merged_df.drop(columns=["main_artist", "artist_clean", "name_original"])

# Guardar
merged_df.to_csv("merged_songs.csv", index=False, encoding="utf-8", quoting=1)