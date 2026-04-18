"""
Data Processing Module for Music Recommendation System

This module handles:
- Loading Spotify tracks dataset from CSV
- Data cleaning and validation
- Feature engineering (combined_features column)
- Data normalization for similarity calculations
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
import os
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MusicDataProcessor:
    """
    Handles all data processing operations for the music recommendation system.
    """

    def __init__(self, csv_path: str):
        """
        Initialize the data processor.

        Args:
            csv_path (str): Path to the Spotify tracks CSV file
        """
        self.csv_path = csv_path
        self.df = None
        self.scaler = StandardScaler()
        self.feature_cols = None

    def load_data(self) -> pd.DataFrame:
        """
        Load the Spotify tracks dataset from CSV.

        Returns:
            pd.DataFrame: The loaded dataset

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            pd.errors.ParserError: If the CSV is malformed
        """
        try:
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"CSV file not found at: {self.csv_path}")

            self.df = pd.read_csv(self.csv_path, low_memory=False)
            logger.info(f"Successfully loaded dataset with {len(self.df)} tracks")
            logger.info(f"Columns: {list(self.df.columns)}")
            return self.df

        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            raise
        except pd.errors.ParserError as e:
            logger.error(f"CSV parsing error: {e}")
            raise

    def clean_data(self) -> pd.DataFrame:
        """
        Clean the dataset by handling missing values and duplicates.

        Returns:
            pd.DataFrame: The cleaned dataset
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        initial_size = len(self.df)

        # Remove duplicates based on track name and artist
        if 'track_name' in self.df.columns and 'artists' in self.df.columns:
            self.df = self.df.drop_duplicates(
                subset=['track_name', 'artists'],
                keep='first'
            )
            logger.info(f"Removed {initial_size - len(self.df)} duplicate records")

        # Handle missing values in critical columns
        critical_cols = ['track_name', 'artists']
        self.df = self.df.dropna(subset=critical_cols)
        logger.info(f"Removed records with missing critical columns. Remaining: {len(self.df)}")

        # Fill numeric missing values with median
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if self.df[col].isna().sum() > 0:
                median_val = self.df[col].median()
                self.df[col].fillna(median_val, inplace=True)
                logger.info(f"Filled missing values in '{col}' with median: {median_val}")

        return self.df

    def engineer_features(self) -> pd.DataFrame:
        """
        Create a combined_features column for similarity calculations.

        This combines multiple audio features to create a comprehensive feature representation:
        - Acousticness, danceability, energy
        - Instrumentalness, liveness, speechiness
        - Valence, loudness, tempo
        - Key, mode

        Returns:
            pd.DataFrame: DataFrame with engineered features

        Raises:
            ValueError: If required audio feature columns are missing
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Define key audio features for recommendation
        required_audio_features = [
            'acousticness', 'danceability', 'energy',
            'instrumentalness', 'liveness', 'speechiness',
            'valence', 'loudness', 'tempo'
        ]

        # Check if required columns exist
        missing_cols = [col for col in required_audio_features if col not in self.df.columns]
        if missing_cols:
            available_features = [col for col in required_audio_features if col in self.df.columns]
            logger.warning(f"Missing features: {missing_cols}. Using available: {available_features}")
            required_audio_features = available_features

        self.feature_cols = required_audio_features

        # Normalize the features
        self.df[required_audio_features] = self.scaler.fit_transform(self.df[required_audio_features])

        # Create combined features as a normalized feature vector
        self.df['combined_features'] = self.df[required_audio_features].values.tolist()

        logger.info(f"Created combined_features with {len(required_audio_features)} audio features")
        logger.info(f"Total records with features: {len(self.df)}")

        return self.df

    def get_processed_data(self, csv_path: Optional[str] = None) -> Tuple[pd.DataFrame, list]:
        """
        Execute the complete data processing pipeline.

        Args:
            csv_path (str, optional): Path to CSV file. If not provided, uses the initialized path.

        Returns:
            Tuple[pd.DataFrame, list]: Processed dataframe and list of feature columns used
        """
        if csv_path:
            self.csv_path = csv_path

        try:
            self.load_data()
            self.clean_data()
            self.engineer_features()
            logger.info("Data processing pipeline completed successfully")
            return self.df, self.feature_cols
        except Exception as e:
            logger.error(f"Error in data processing pipeline: {e}")
            raise

    def get_track_by_name(self, track_name: str) -> Optional[pd.Series]:
        """
        Retrieve a track by its name (case-insensitive).

        Args:
            track_name (str): Name of the track to find

        Returns:
            pd.Series or None: The track row if found, None otherwise
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Case-insensitive search
        matches = self.df[self.df['track_name'].str.lower() == track_name.lower()]

        if len(matches) == 0:
            return None
        elif len(matches) > 1:
            logger.warning(f"Found {len(matches)} matches for '{track_name}'. Returning first match.")

        return matches.iloc[0]

    def get_all_track_names(self) -> list:
        """
        Get a list of all available track names.

        Returns:
            list: List of all track names in the dataset
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        return self.df['track_name'].tolist()
