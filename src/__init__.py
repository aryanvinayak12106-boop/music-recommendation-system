"""
Music Recommendation System
A content-based music recommendation engine using Spotify track audio features.
"""

__version__ = '1.0.0'
__author__ = 'Music Recommendation Team'

from .data_processor import MusicDataProcessor
from .similarity_engine import SimilarityEngine

__all__ = ['MusicDataProcessor', 'SimilarityEngine']
