"""
Similarity Engine for Music Recommendation System

This module implements:
- Cosine similarity-based track matching
- Nearest neighbors search
- Similarity scoring and ranking
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """
    Computes similarity between tracks using audio features and finds nearest neighbors.
    """

    def __init__(self, dataframe: pd.DataFrame, feature_column: str = 'combined_features'):
        """
        Initialize the similarity engine with processed music data.

        Args:
            dataframe (pd.DataFrame): DataFrame containing track data with features
            feature_column (str): Name of the column containing feature vectors
        """
        self.df = dataframe.reset_index(drop=True)
        self.feature_column = feature_column
        self.knn_model = None
        self.features_matrix = None
        self._build_features_matrix()
        self._build_knn_model()
        logger.info(f"Similarity engine initialized with {len(self.df)} tracks")

    def _build_features_matrix(self) -> None:
        """
        Convert the combined_features column into a 2D numpy array.
        This matrix will be used for similarity calculations.
        """
        try:
            # Convert list of features to 2D numpy array
            self.features_matrix = np.array(
                self.df[self.feature_column].tolist()
            )
            logger.info(f"Features matrix shape: {self.features_matrix.shape}")
        except Exception as e:
            logger.error(f"Error building features matrix: {e}")
            raise

    def _build_knn_model(self) -> None:
        """
        Build a NearestNeighbors model using cosine distance metric.
        This enables efficient similarity searching.
        """
        try:
            # Use cosine distance (which equals 1 - cosine_similarity)
            self.knn_model = NearestNeighbors(
                n_neighbors=min(6, len(self.df)),  # +1 to include the query track itself
                metric='cosine',
                n_jobs=-1  # Use all available processors
            )
            self.knn_model.fit(self.features_matrix)
            logger.info("KNN model built successfully using cosine distance metric")
        except Exception as e:
            logger.error(f"Error building KNN model: {e}")
            raise

    def get_cosine_similarity(self, track_index: int, target_index: int) -> float:
        """
        Calculate cosine similarity between two tracks using their feature vectors.

        Mathematical formula:
        cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)

        Args:
            track_index (int): Index of the first track
            target_index (int): Index of the second track

        Returns:
            float: Cosine similarity score between 0 and 1 (higher = more similar)
        """
        try:
            track_features = self.features_matrix[track_index].reshape(1, -1)
            target_features = self.features_matrix[target_index].reshape(1, -1)

            similarity = cosine_similarity(track_features, target_features)[0][0]
            return float(similarity)
        except IndexError as e:
            logger.error(f"Index out of range: {e}")
            raise

    def find_similar_tracks(
        self,
        track_index: int,
        n_recommendations: int = 5
    ) -> List[Tuple[int, str, str, float]]:
        """
        Find the most similar tracks to a given track using NearestNeighbors.

        Args:
            track_index (int): Index of the query track
            n_recommendations (int): Number of recommendations to return (excluding the query track)

        Returns:
            List[Tuple[int, str, str, float]]: List of tuples containing:
                - Track index
                - Track name
                - Artists
                - Similarity score (0-1)

        Raises:
            IndexError: If track_index is out of range
        """
        if track_index < 0 or track_index >= len(self.df):
            raise IndexError(f"Track index {track_index} out of range [0, {len(self.df)-1}]")

        try:
            # Query KNN model (+1 to include the track itself which we'll exclude)
            distances, indices = self.knn_model.kneighbors(
                self.features_matrix[track_index].reshape(1, -1),
                n_neighbors=min(n_recommendations + 1, len(self.df))
            )

            # Convert distances to similarity scores (cosine_distance = 1 - cosine_similarity)
            similarities = 1 - distances[0]

            recommendations = []
            for idx, similarity in zip(indices[0], similarities):
                # Skip the query track itself
                if idx == track_index:
                    continue

                track_row = self.df.iloc[idx]
                recommendations.append((
                    idx,
                    track_row['track_name'],
                    track_row['artists'],
                    float(similarity)
                ))

                # Stop after getting n_recommendations
                if len(recommendations) == n_recommendations:
                    break

            logger.info(f"Found {len(recommendations)} recommendations for track index {track_index}")
            return recommendations

        except Exception as e:
            logger.error(f"Error finding similar tracks: {e}")
            raise

    def recommend_by_track_name(
        self,
        track_name: str,
        dataframe: pd.DataFrame,
        n_recommendations: int = 5
    ) -> List[Tuple[str, str, float]]:
        """
        Find similar tracks by track name.

        Args:
            track_name (str): Name of the track to find recommendations for
            dataframe (pd.DataFrame): Original dataframe with track_name column
            n_recommendations (int): Number of recommendations to return

        Returns:
            List[Tuple[str, str, float]]: List of (track_name, artists, similarity_score) tuples

        Raises:
            ValueError: If track not found in dataset
        """
        # Find the track index by name
        matches = dataframe[dataframe['track_name'].str.lower() == track_name.lower()]

        if len(matches) == 0:
            raise ValueError(f"Track '{track_name}' not found in dataset")

        track_index = matches.index[0]
        logger.info(f"Found track '{track_name}' at index {track_index}")

        # Get similar tracks
        similar_tracks = self.find_similar_tracks(track_index, n_recommendations)

        # Return formatted results
        return [
            (name, artists, score) for _, name, artists, score in similar_tracks
        ]

    def get_similarity_matrix(self) -> np.ndarray:
        """
        Compute the full cosine similarity matrix for all tracks.

        Returns:
            np.ndarray: 2D array of shape (n_tracks, n_tracks) with similarity scores

        Note: This can be memory-intensive for large datasets (>10,000 tracks)
        """
        try:
            similarity_matrix = cosine_similarity(self.features_matrix)
            logger.info(f"Computed similarity matrix with shape {similarity_matrix.shape}")
            return similarity_matrix
        except Exception as e:
            logger.error(f"Error computing similarity matrix: {e}")
            raise
