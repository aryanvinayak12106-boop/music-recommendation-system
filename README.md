# Music Recommendation System

A content-based music recommendation engine that uses Spotify track audio features to recommend similar songs. Built with scikit-learn for similarity calculations and feature processing.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [API Documentation](#api-documentation)
- [Examples](#examples)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)

---

## Features

✅ **Content-Based Recommendations** - Uses 9 audio features for similarity calculations  
✅ **Efficient Similarity Search** - NearestNeighbors with cosine distance metric  
✅ **Data Cleaning** - Automatic handling of missing values and duplicates  
✅ **Feature Normalization** - StandardScaler normalization for all audio features  
✅ **Interactive CLI** - User-friendly command-line interface  
✅ **Error Handling** - Robust error handling for missing tracks  
✅ **Fully Documented** - Comprehensive docstrings and logging  

---

## Project Structure

```
music-recommendation-system/
├── data/                          # Data folder (place your CSV here)
│   └── spotify_tracks.csv         # Spotify dataset (not included)
├── src/                           # Source code
│   ├── __init__.py                # Package initialization
│   ├── data_processor.py          # Data loading and feature engineering
│   ├── similarity_engine.py       # Similarity calculations and recommendations
│   └── recommend.py               # CLI interface
├── notebooks/                     # Jupyter notebooks (analysis notebooks go here)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone/Navigate to the project directory:**
   ```bash
   cd music-recommendation-system
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Place your Spotify dataset:**
   - Download the `spotify_tracks.csv` from Kaggle or your data source
   - Place it in the `data/` folder at: `data/spotify_tracks.csv`

---

## Quick Start

### Interactive Mode

Run the CLI in interactive mode to search for tracks:

```bash
cd src
python recommend.py --data-path ../data/spotify_tracks.csv
```

Then follow the prompts to search for tracks and get recommendations.

### Non-Interactive Mode (Direct Recommendation)

Get recommendations for a specific track directly:

```bash
cd src
python recommend.py --data-path ../data/spotify_tracks.csv --track "Bohemian Rhapsody"
```

### Custom Number of Recommendations

Get a different number of recommendations:

```bash
python recommend.py --data-path ../data/spotify_tracks.csv --track "Shape of You" --recommendations 10
```

---

## How It Works

### 1. Data Processing Pipeline

```
CSV File → Load Data → Clean Data → Feature Engineering → Similarity Search
```

#### Step 1: **Data Loading** (`load_data()`)
- Reads the Spotify tracks CSV file
- Validates file existence and format
- Logs dataset dimensions

#### Step 2: **Data Cleaning** (`clean_data()`)
- Removes duplicate tracks (by track name and artist)
- Drops records with missing critical columns (track_name, artists)
- Fills numeric missing values with median imputation
- Ensures high-quality data for modeling

#### Step 3: **Feature Engineering** (`engineer_features()`)
- Extracts 9 key audio features from the dataset:
  - **Acousticness** (0-1): How acoustic the track is
  - **Danceability** (0-1): How suitable for dancing
  - **Energy** (0-1): Intensity and activity level
  - **Instrumentalness** (0-1): Presence of vocals
  - **Liveness** (0-1): Audience presence
  - **Speechiness** (0-1): Presence of spoken words
  - **Valence** (0-1): Musical positiveness/happiness
  - **Loudness** (dB): Overall loudness
  - **Tempo** (BPM): Speed of the track

- Normalizes features using StandardScaler (mean=0, std=1)
- Combines all normalized features into a single feature vector per track

### 2. Similarity Calculation

The system uses **Cosine Similarity** to measure track similarity:

$$\text{cosine\_similarity}(A, B) = \frac{A \cdot B}{||A|| \times ||B||} = \frac{\sum_{i=1}^{n} A_i \times B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}}$$

**Why Cosine Similarity?**
- Measures angular distance between feature vectors
- Range: 0 to 1 (1 = identical features)
- Robust to feature magnitude differences
- Efficient for high-dimensional data
- Industry standard for music recommendations

### 3. Nearest Neighbors Search

The system uses scikit-learn's `NearestNeighbors` with:
- **Metric:** Cosine distance (1 - cosine similarity)
- **Algorithm:** Auto (optimized based on data)
- **Parallelization:** Multi-core processing for speed

For a query track, it:
1. Extracts the track's feature vector
2. Finds the k+1 nearest neighbors (k recommendations + 1 for the track itself)
3. Excludes the query track from results
4. Converts distances back to similarity scores (1 - distance)
5. Returns top-5 most similar tracks

---

## API Documentation

### `MusicDataProcessor`

**Class for data loading, cleaning, and feature engineering.**

#### Methods:

| Method | Description | Returns |
|--------|-------------|---------|
| `load_data()` | Load CSV file | `pd.DataFrame` |
| `clean_data()` | Clean and validate data | `pd.DataFrame` |
| `engineer_features()` | Create combined feature vectors | `pd.DataFrame` |
| `get_processed_data()` | Execute full pipeline | `Tuple[pd.DataFrame, list]` |
| `get_track_by_name(track_name)` | Find track by name | `pd.Series` or `None` |
| `get_all_track_names()` | Get all track names | `list` |

#### Example:
```python
from data_processor import MusicDataProcessor

processor = MusicDataProcessor('data/spotify_tracks.csv')
df, features = processor.get_processed_data()
print(f"Loaded {len(df)} tracks with {len(features)} features")
```

### `SimilarityEngine`

**Class for similarity calculations and recommendations.**

#### Methods:

| Method | Description | Returns |
|--------|-------------|---------|
| `get_cosine_similarity(idx1, idx2)` | Calculate cosine similarity between two tracks | `float` |
| `find_similar_tracks(track_index, n)` | Find n most similar tracks | `List[Tuple]` |
| `recommend_by_track_name(name, df, n)` | Get recommendations by track name | `List[Tuple]` |
| `get_similarity_matrix()` | Compute full similarity matrix | `np.ndarray` |

#### Example:
```python
from similarity_engine import SimilarityEngine
from data_processor import MusicDataProcessor

processor = MusicDataProcessor('data/spotify_tracks.csv')
df, _ = processor.get_processed_data()

engine = SimilarityEngine(df)
recommendations = engine.recommend_by_track_name('Shape of You', df, 5)

for track_name, artists, similarity in recommendations:
    print(f"{track_name} by {artists} (Similarity: {similarity:.2%})")
```

---

## Examples

### Example 1: Get Recommendations via Python Script

```python
from src.data_processor import MusicDataProcessor
from src.similarity_engine import SimilarityEngine

# Load and process data
processor = MusicDataProcessor('data/spotify_tracks.csv')
df, features = processor.get_processed_data()

# Initialize engine
engine = SimilarityEngine(df)

# Get recommendations
recommendations = engine.recommend_by_track_name('Blinding Lights', df, 5)

# Display results
for i, (track_name, artists, score) in enumerate(recommendations, 1):
    print(f"{i}. {track_name} by {artists}")
    print(f"   Similarity: {score:.1%}\n")
```

### Example 2: Calculate Similarity Between Two Specific Tracks

```python
# Find track indices
track1 = df[df['track_name'].str.contains('Hotel California', case=False)].index[0]
track2 = df[df['track_name'].str.contains('Stairway to Heaven', case=False)].index[0]

# Calculate similarity
similarity = engine.get_cosine_similarity(track1, track2)
print(f"Similarity between tracks: {similarity:.2%}")
```

### Example 3: Batch Recommendations

```python
# Get recommendations for multiple tracks
query_tracks = ['Bohemian Rhapsody', 'Let It Be', 'Imagine']

for query in query_tracks:
    try:
        recs = engine.recommend_by_track_name(query, df, 3)
        print(f"\n{query}:")
        for name, artists, score in recs:
            print(f"  → {name} ({score:.1%})")
    except ValueError as e:
        print(f"Error for '{query}': {e}")
```

---

## Technical Details

### Feature Normalization

All audio features are normalized using **StandardScaler**:
- Centers features to mean=0
- Scales to standard deviation=1
- Prevents high-magnitude features from dominating similarity
- Enables fair comparison across different feature ranges

### Distance Metric

**Cosine Distance** = 1 - Cosine Similarity

Advantages:
- Focuses on direction (feature patterns), not magnitude
- Interpretable (0 = identical, 1 = orthogonal)
- Efficient for sparse/dense vectors
- Works well with normalized features

### Time Complexity

- **Data Processing:** O(n) where n = number of tracks
- **KNN Model Building:** O(n log n)
- **Single Recommendation Query:** O(k log n) where k = n_neighbors
- **Full Similarity Matrix:** O(n²) - memory intensive for large datasets

### Space Complexity

- **Features Matrix:** O(n × m) where m = 9 (number of features)
- **KNN Model:** O(n × m)
- **Full Similarity Matrix:** O(n²) - only compute if necessary

---

## Error Handling

The system includes comprehensive error handling:

### Track Not Found
```python
try:
    recs = engine.recommend_by_track_name('NonexistentTrack', df)
except ValueError as e:
    print(f"Track not found: {e}")
```

### Invalid CSV Path
```python
try:
    processor = MusicDataProcessor('invalid/path.csv')
    processor.load_data()
except FileNotFoundError as e:
    print(f"CSV file error: {e}")
```

### Index Out of Range
```python
try:
    similarity = engine.get_cosine_similarity(99999, 0)
except IndexError as e:
    print(f"Invalid track index: {e}")
```

---

## Troubleshooting

### Issue: "CSV file not found"
**Solution:** Ensure `spotify_tracks.csv` is in the `data/` folder
```bash
ls data/  # Check if file exists
```

### Issue: No tracks found when searching
**Solution:** The search is case-insensitive, but track names must be exact (partial matching supported)
```python
# These will work:
# "Shape of You"
# "shape"
# "of you"
```

### Issue: Memory error with full similarity matrix
**Solution:** Don't compute full similarity matrix for large datasets. Use `find_similar_tracks()` instead:
```python
# ❌ Avoid for large datasets:
similarity_matrix = engine.get_similarity_matrix()

# ✅ Use this instead:
recommendations = engine.find_similar_tracks(track_index, 5)
```

### Issue: Slow recommendations
**Solution:** This is normal for cold starts. The NearestNeighbors model caches results. Subsequent queries are faster.

### Issue: Different results each time
**Solution:** This is expected with cosine similarity - same tracks get exact same recommendations. If you want randomness, use a different algorithm.

---

## Performance Tips

1. **Use NearestNeighbors** instead of full similarity matrix for large datasets
2. **Request fewer recommendations** (5-10) to speed up queries
3. **Run on multi-core** systems (n_jobs=-1 enabled by default)
4. **Cache processed data** if running multiple queries
5. **Use track indices** when possible instead of searching by name

---

## Dataset Requirements

The CSV file should contain these columns:
- `track_name` (str): Name of the track
- `artists` (str): Artist(s) name
- `acousticness` (float, 0-1)
- `danceability` (float, 0-1)
- `energy` (float, 0-1)
- `instrumentalness` (float, 0-1)
- `liveness` (float, 0-1)
- `speechiness` (float, 0-1)
- `valence` (float, 0-1)
- `loudness` (float, dB)
- `tempo` (float, BPM)

---

## Future Enhancements

- [ ] Collaborative filtering integration
- [ ] Hybrid recommendations (content + collaborative)
- [ ] Genre-based filtering
- [ ] Mood-based recommendations
- [ ] Web API interface
- [ ] Machine learning model for personalization
- [ ] Real-time Spotify API integration
- [ ] User preference learning

---

## License

This project is open source and available under the MIT License.

---

## Author

Built as a Senior Machine Learning Engineer project for content-based music recommendation.

For questions or contributions, please refer to the code documentation and docstrings in the source files.
