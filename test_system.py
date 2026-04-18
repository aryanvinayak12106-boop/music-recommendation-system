"""Quick test of the recommendation system with your dataset"""
import sys
sys.path.insert(0, r'c:\Users\Aryan salunkhe\OneDrive\Documents\Projects\music-recommendation-system\src')

from data_processor import MusicDataProcessor
from similarity_engine import SimilarityEngine

# Initialize the system
print("="*80)
print("TESTING MUSIC RECOMMENDATION SYSTEM WITH YOUR DATASET")
print("="*80)

csv_path = r'c:\Users\Aryan salunkhe\OneDrive\Documents\Projects\music-recommendation-system\data\spotify_tracks.csv'

# Process data
print("\n1. Loading and processing data...")
processor = MusicDataProcessor(csv_path)
df, features = processor.get_processed_data()

print(f"✓ Dataset loaded: {len(df)} tracks with {len(features)} features")
print(f"Track names sample: {df['track_name'].head(3).tolist()}")

# Initialize similarity engine
print("\n2. Building similarity engine...")
engine = SimilarityEngine(df)
print("✓ Similarity engine ready!")

# Get recommendations for a track
print("\n3. Getting recommendations for the first track...")
first_track = df.iloc[0]['track_name']
print(f"Query track: '{first_track}'")

try:
    recommendations = engine.recommend_by_track_name(first_track, df, 5)
    print(f"\n✓ Top 5 Recommendations:")
    print(f"{'Rank':<6} {'Track Name':<40} {'Artists':<30} {'Similarity':<10}")
    print("-"*90)
    
    for rank, (name, artists, score) in enumerate(recommendations, 1):
        name_short = name[:39] if len(name) > 39 else name
        artists_short = artists[:29] if len(artists) > 29 else artists
        print(f"{rank:<6} {name_short:<40} {artists_short:<30} {score*100:>6.1f}%")
    
    print("\n" + "="*80)
    print("✓ SYSTEM TEST SUCCESSFUL!")
    print("="*80)
    print("\nYou can now use the CLI to get recommendations:")
    print("  cd src")
    print("  python recommend.py --data-path ../data/spotify_tracks.csv")
    
except Exception as e:
    print(f"Error: {e}")
