# Designing a Domain-Specific Search Engine Using a Data Warehouse
### FCUL — Information Integration and Analytic Data Processing (2025/2026)

**Professora:** Márcia Barros

**Group 5**
- Nuno Lages — 66091
- Nuno Rosado — 66104
- Diogo Carvalho — 66123

---

### Overview

This repository contains the implementation of a **domain-specific search engine backed by a data warehouse**, developed for the Information Integration and Analytic Data Processing course. The chosen domain is the **music ecosystem**, combining structured data from **Spotify** (tracks and artists) with critical reviews from **Pitchfork**, and enriched with precise release dates via the **MusicBrainz API**.

The project covers the full pipeline: data integration and ETL, dimensional modeling, physical data warehouse design, document extraction, text preprocessing, retrieval model implementation, evaluation, Learning to Rank, and a bonus Retrieval-Augmented Generation (RAG) module.

---

### Datasets

| Dataset | Source | Records | Description |
|---|---|---|---|
| 550K Spotify Songs — Songs | [Kaggle](https://www.kaggle.com/datasets/serkantysz/550k-spotify-songs-audio-lyrics-and-genres) | 550,622 | Track metadata, lyrics, genres, and audio features |
| 550K Spotify Songs — Artists | [Kaggle](https://www.kaggle.com/datasets/serkantysz/550k-spotify-songs-audio-lyrics-and-genres) | 71,440 | Artist name, followers, popularity, genres |
| Pitchfork Reviews | [Kaggle](https://www.kaggle.com/datasets/timstafford/pitchfork-reviews) | 25,708 | Album reviews, scores, summaries |

Datasets are not included in this repository (see `.gitignore`) and should be placed under a local `data/` folder before running the pipeline.

---

### Project Structure

```
├── Code.ipynb                        Main notebook — full pipeline (ETL to RAG)
├── scripts/
│   ├── musicbrainzAPI.py             Enriches songs with precise release dates via MusicBrainz API
│   ├── remove_musics_without_review.py   Filters songs to only those with an associated Pitchfork review
│   ├── music_combiner.py             Merges enriched release dates back into the main songs dataset
│   └── test.py                       Auxiliary/sanity-check script
├── jsons/
│   └── contractions_en.json          Lookup map for expanding negative contractions during preprocessing
├── requirements.txt                  Python dependencies
└── README.md
```

---

### Pipeline

#### 1. ETL Process
Data is extracted from the three source CSVs into pandas DataFrames. Songs belonging to albums without an associated review are filtered out (`remove_musics_without_review.py`), and release dates are enriched via the MusicBrainz API (`musicbrainzAPI.py`, `music_combiner.py`). During transformation, duplicates and nulls are removed, and artist/album/track names are normalized (lowercased, trimmed, accents removed) to guarantee consistent joins across sources.

#### 2. Dimensional Modeling
A star schema (with a snowflake extension for Album → Review) was designed with the following grain: **one row per individual music track associated with an artist, an album, a genre, and a specific release date.**

- **Fact table:** audio features (danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness), duration, music popularity, and word count.
- **Dimensions:** `Music`, `Artist`, `Album`, `Review`, `Genre`, `Date`.

#### 3. Physical Data Warehouse
Implemented in **PostgreSQL**. Surrogate keys are used as primary keys for every dimension, referential integrity is enforced between the fact table and dimensions, and B-Tree indexes are created on foreign keys and high-cardinality analytical columns (e.g. `music_popularity`, review score) to speed up joins and filtering.

#### 4. Searchable Document Extraction
Two linked document types are generated from the warehouse (joined via `music_id`):
- **Textual documents** — title, release date, artist, album, genre, lyrics, and aggregated album reviews (summary + full text), used for text retrieval.
- **Measure documents** — normalized numeric features (audio features, popularity, review score, word count), used for analytical filtering and ranking.

A field-weighting strategy is applied when building the text index (title ×5, artist ×4, lyrics ×3, reviews ×2, genre ×2) to prioritize the most discriminative fields.

#### 5. Text Preprocessing
Each document is cleaned (Unicode normalization, lowercasing, punctuation removal), had contractions expanded, tokenized, stripped of stop words, and stemmed. Documents are then vectorized using **TF-IDF**. Measure documents are normalized per feature scale (min-max, Z-score, or log-transform depending on the metric).

#### 6. Retrieval Models
Three retrieval models were implemented and compared:
- Boolean Retrieval (AND / OR)
- TF-IDF (Vector Space Model)
- BM25

#### 7. Evaluation
A stratified sample of 400 documents (fixed seed = 42) was used to build 20 evaluation queries with relevance judgments (qrels, scale 0–3). TF-IDF and BM25 were evaluated at k=5 using Precision, Recall, F1, MAP, and nDCG.

#### 8. Learning to Rank
A **Gradient Boosting Regressor** was trained on 13 features (TF-IDF score, BM25 score, and 11 warehouse metrics such as danceability, energy, and popularity), using the qrels as training labels.

#### Bonus: Retrieval-Augmented Generation (RAG)
An LLM (via the **Groq API**) is used both to parse natural language queries into structured numeric filters (e.g. "popular tracks" → `{"music_popularity": {"gt": 0.7}}`) and to generate a conversational, justified response from the top-ranked results, turning the retrieval system into an interactive music assistant.

---

### Requirements

- Python 3.10+
- PostgreSQL
- A `.env` file with a `GROQ_API_KEY` (required for the RAG bonus step)

Install dependencies:
```bash
pip install -r requirements.txt
```

Main dependencies: `numpy`, `pandas`, `sqlalchemy`, `psycopg2`, `scikit-learn`, `nltk`, `groq`, `dotenv`.

### Running the Project

1. Place the raw datasets (`songs.csv`, `artists.csv`, `pitchfork_reviews.csv`) inside a local `data/` folder.
2. Run the preprocessing scripts in order:
   ```bash
   python scripts/remove_musics_without_review.py
   python scripts/musicbrainzAPI.py
   python scripts/music_combiner.py
   ```
3. Open and run `Code.ipynb` to execute the full ETL, warehouse loading, document extraction, retrieval, evaluation, and RAG pipeline.
