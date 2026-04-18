"""
Music Recommendation CLI

Interactive command-line interface for getting music recommendations based on a track.
Allows users to input a track name and get the top 5 most similar tracks.

Usage:
    python recommend.py --data-path <path_to_csv>
"""

import argparse
import logging
import sys
import os
from typing import Optional
from pathlib import Path

from data_processor import MusicDataProcessor
from similarity_engine import SimilarityEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicRecommendationCLI:
    """
    Command-line interface for the music recommendation system.
    """

    def __init__(self, csv_path: str):
        """
        Initialize the CLI by loading and processing data.

        Args:
            csv_path (str): Path to the Spotify tracks CSV file
        """
        self.csv_path = csv_path
        self.processor = None
        self.engine = None
        self.df = None

        self._initialize_system()

    def _initialize_system(self) -> None:
        """
        Initialize the recommendation system by loading and processing data.
        """
        try:
            logger.info("Initializing music recommendation system...")

            # Initialize data processor
            self.processor = MusicDataProcessor(self.csv_path)
            self.df, _ = self.processor.get_processed_data()

            # Initialize similarity engine
            self.engine = SimilarityEngine(self.df)

            logger.info("System initialized successfully!")
            print("\n" + "="*70)
            print("Music Recommendation System Ready".center(70))
            print("="*70)
            print(f"Loaded {len(self.df)} tracks\n")

        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error initializing system: {e}")
            sys.exit(1)

    def search_track(self, query: str) -> list:
        """
        Search for tracks by partial name match.

        Args:
            query (str): Partial track name to search for

        Returns:
            list: List of matching track names
        """
        matches = self.df[
            self.df['track_name'].str.contains(query, case=False, na=False)
        ]['track_name'].unique().tolist()

        return matches[:10]  # Return top 10 matches

    def get_recommendations(self, track_name: str, n_recommendations: int = 5) -> Optional[list]:
        """
        Get recommendations for a given track.

        Args:
            track_name (str): Name of the track
            n_recommendations (int): Number of recommendations to return

        Returns:
            Optional[list]: List of recommended tracks or None if track not found
        """
        try:
            recommendations = self.engine.recommend_by_track_name(
                track_name,
                self.df,
                n_recommendations
            )
            return recommendations

        except ValueError as e:
            logger.error(f"Error: {e}")
            return None

    def display_recommendations(self, track_name: str, recommendations: list) -> None:
        """
        Display recommendations in a formatted table.

        Args:
            track_name (str): Original track name
            recommendations (list): List of recommended tracks
        """
        print("\n" + "="*70)
        print(f"Top 5 Recommendations for: '{track_name}'".center(70))
        print("="*70)
        print(f"\n{'Rank':<6} {'Track Name':<30} {'Artists':<25} {'Similarity':<8}")
        print("-"*70)

        for rank, (rec_name, artists, similarity) in enumerate(recommendations, 1):
            # Truncate long text for display
            disp_name = rec_name[:29] if len(rec_name) > 29 else rec_name
            disp_artists = artists[:24] if len(artists) > 24 else artists

            similarity_pct = f"{similarity*100:.1f}%"
            print(f"{rank:<6} {disp_name:<30} {disp_artists:<25} {similarity_pct:<8}")

        print("-"*70 + "\n")

    def search_and_ask(self, partial_name: str) -> Optional[str]:
        """
        Search for tracks and let user select one if multiple matches found.

        Args:
            partial_name (str): Partial track name

        Returns:
            Optional[str]: Selected track name or None if no match
        """
        matches = self.search_track(partial_name)

        if not matches:
            logger.warning(f"No tracks found matching '{partial_name}'")
            return None

        if len(matches) == 1:
            return matches[0]

        # Multiple matches - let user choose
        print(f"\nFound {len(matches)} matching tracks:")
        print("-" * 70)
        for idx, track in enumerate(matches, 1):
            print(f"{idx}. {track}")

        while True:
            try:
                choice = input("\nSelect a track (enter number) or 0 to cancel: ").strip()
                choice_idx = int(choice) - 1

                if choice == "0":
                    return None

                if 0 <= choice_idx < len(matches):
                    return matches[choice_idx]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def run_interactive(self) -> None:
        """
        Run the interactive recommendation loop.
        """
        print("\nCommands:")
        print("  'quit' or 'exit' - Exit the application")
        print("  'help' - Show available commands")
        print("  Or enter a track name to get recommendations\n")

        while True:
            try:
                user_input = input("Enter track name (or 'quit' to exit): ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nThank you for using the Music Recommendation System!")
                    break

                if user_input.lower() == 'help':
                    print("\nHow to use:")
                    print("1. Type a track name to get recommendations")
                    print("2. If multiple matches exist, select one")
                    print("3. View the top 5 most similar tracks")
                    print("4. Type 'quit' to exit\n")
                    continue

                # Search for track
                track_name = self.search_and_ask(user_input)

                if not track_name:
                    print("Recommendation cancelled.\n")
                    continue

                # Get and display recommendations
                recommendations = self.get_recommendations(track_name)

                if recommendations is None:
                    print(f"\nSorry, could not find recommendations for '{track_name}'.\n")
                    continue

                self.display_recommendations(track_name, recommendations)

            except KeyboardInterrupt:
                print("\n\nExiting... Goodbye!")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"An error occurred: {e}. Please try again.\n")

    def recommend_single(self, track_name: str) -> None:
        """
        Get a single recommendation without entering interactive mode.

        Args:
            track_name (str): Name of the track
        """
        track = self.search_and_ask(track_name)

        if not track:
            print(f"Track not found: {track_name}")
            return

        recommendations = self.get_recommendations(track)

        if recommendations is None:
            print(f"Could not find recommendations for '{track}'")
            return

        self.display_recommendations(track, recommendations)


def main():
    """
    Main entry point for the CLI application.
    """
    parser = argparse.ArgumentParser(
        description='Music Recommendation System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python recommend.py --data-path data/spotify_tracks.csv
  python recommend.py --data-path data/spotify_tracks.csv --track "Song Name"
        """
    )

    parser.add_argument(
        '--data-path',
        type=str,
        required=True,
        help='Path to the Spotify tracks CSV file'
    )

    parser.add_argument(
        '--track',
        type=str,
        default=None,
        help='Optional: Provide a track name directly (non-interactive mode)'
    )

    parser.add_argument(
        '--recommendations',
        type=int,
        default=5,
        help='Number of recommendations to return (default: 5)'
    )

    args = parser.parse_args()

    # Validate CSV path
    if not os.path.exists(args.data_path):
        logger.error(f"CSV file not found: {args.data_path}")
        sys.exit(1)

    # Initialize CLI
    cli = MusicRecommendationCLI(args.data_path)

    # If track provided, run in single-query mode
    if args.track:
        cli.recommend_single(args.track)
    else:
        # Run interactive mode
        cli.run_interactive()


if __name__ == '__main__':
    main()
