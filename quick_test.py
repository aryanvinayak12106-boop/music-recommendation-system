"""Simple quick test - just load data"""
import pandas as pd
import os

csv_path = r'c:\Users\Aryan salunkhe\OneDrive\Documents\Projects\music-recommendation-system\data\spotify_tracks.csv'

if os.path.exists(csv_path):
    print("✓ Dataset file found!")
    df = pd.read_csv(csv_path)
    print(f"✓ Dataset loaded: {len(df)} tracks")
    print(f"\nColumns available: {list(df.columns)}")
    print(f"\nFirst 3 tracks:")
    for i in range(min(3, len(df))):
        track = df.iloc[i]
        print(f"  {i+1}. '{track['track_name']}' by {track['artists']}")
    print("\n✓ YOUR DATASET IS READY TO USE!")
    print("\nRun the recommendation system:")
    print("  cd src")
    print("  python recommend.py --data-path ../data/spotify_tracks.csv")
else:
    print("✗ Dataset not found!")
