"""
Flask API wrapper for the Music Recommendation System
Run with: python api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from src.data_processor import MusicDataProcessor
from src.similarity_engine import SimilarityEngine
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Load data and models at startup
DATA_PATH = 'data/spotify_tracks.csv'
processor = None
engine = None

def load_models():
    """Load data processor and similarity engine"""
    global processor, engine
    try:
        logger.info("Loading data...")
        processor = MusicDataProcessor(DATA_PATH)
        df, feature_cols = processor.get_processed_data()
        
        logger.info("Building similarity engine...")
        engine = SimilarityEngine(df)
        
        logger.info(f"✅ Models loaded successfully! Dataset: {len(df)} tracks")
        return True
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': processor is not None and engine is not None
    })

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Get recommendations for a track"""
    try:
        data = request.get_json()
        track_name = data.get('trackName', '').strip()
        num_recommendations = int(data.get('recommendations', 5))
        
        if not track_name:
            return jsonify({'error': 'Track name is required'}), 400
        
        if not processor or not engine:
            return jsonify({'error': 'Models not loaded'}), 500
        
        # Get recommendations
        recommendations_data = engine.recommend_by_track_name(
            track_name, 
            processor.get_processed_data()[0],  # Get the dataframe
            num_recommendations
        )
        
        if not recommendations_data:
            return jsonify({
                'error': f'Track "{track_name}" not found in database',
                'recommendations': []
            }), 404
        
        # Format response
        formatted_recs = []
        for rec in recommendations_data:
            formatted_recs.append({
                'name': rec[1],  # track name
                'artists': rec[2],  # artists
                'similarity': round(float(rec[3]), 3),  # similarity score
                'features': {
                    'energy': round(float(rec[4].get('energy', 0)), 2),
                    'danceability': round(float(rec[4].get('danceability', 0)), 2),
                    'valence': round(float(rec[4].get('valence', 0)), 2),
                    'tempo': round(float(rec[4].get('tempo', 0)), 2),
                }
            })
        
        return jsonify({'recommendations': formatted_recs})
    
    except ValueError as e:
        # Track not found in database
        error_msg = str(e)
        logger.warning(f"Track not found: {error_msg}")
        return jsonify({'error': error_msg}), 404
    
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Search for tracks by name"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip().lower()
        limit = int(data.get('limit', 10))
        
        if not query:
            return jsonify({'tracks': []})
        
        if not processor:
            return jsonify({'error': 'Models not loaded'}), 500
        
        df = processor.get_processed_data()[0]
        
        # Search in track names
        matches = df[df['name'].str.lower().str.contains(query, na=False)]
        
        results = [
            {
                'name': row['name'],
                'artists': row['artists'],
                'id': idx
            }
            for idx, (_, row) in enumerate(matches.head(limit).iterrows())
        ]
        
        return jsonify({'tracks': results})
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get dataset statistics"""
    try:
        if not processor:
            return jsonify({'error': 'Models not loaded'}), 500
        
        df = processor.get_processed_data()[0]
        
        return jsonify({
            'total_tracks': len(df),
            'total_artists': df['artists'].nunique(),
            'status': 'ready'
        })
    
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# Attempt to load models at module import time
# This is necessary for gunicorn to have models ready
try:
    logger.info("⏳ Loading models at startup...")
    load_models()
except Exception as e:
    logger.error(f"⚠️ Models will be loaded on first request: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🎵 API ready at http://0.0.0.0:{port}")
    logger.info(f"Test: POST http://0.0.0.0:{port}/api/recommend")
    logger.info("With body: {\"trackName\": \"Shape of You\", \"recommendations\": 5}")
    app.run(debug=False, host='0.0.0.0', port=port)
