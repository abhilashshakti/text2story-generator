import requests
import json
from config import Config
from typing import List, Dict, Optional
import random

class AudioService:
    def __init__(self):
        self.jamendo_api_key = Config.JAMENDO_API_KEY
    
    def search_audio(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for audio using Jamendo API and curated fallbacks
        """
        print(f"Searching for audio with query: {query}")
        
        audio_files = []
        
        # Try Jamendo Music API first
        if self.jamendo_api_key:
            jamendo_audio = self._search_jamendo_audio(query, count)
            audio_files.extend(jamendo_audio)
        
        # If not enough, use curated free music
        if len(audio_files) < count:
            curated_audio = self._get_curated_audio(query, count - len(audio_files))
            audio_files.extend(curated_audio)
        
        print(f"Returning {len(audio_files[:count])} audio files")
        return audio_files[:count]
    
    def _search_jamendo_audio(self, query: str, count: int) -> List[Dict]:
        """Search for free music using Jamendo API"""
        try:
            url = "https://api.jamendo.com/v3/tracks/"
            params = {
                'client_id': self.jamendo_api_key,
                'format': 'json',
                'search': query,
                'limit': count,
                'groupby': 'artist_id',
                'include': 'musicinfo',
                'fuzzytags': 1,
                'license_cc0': 1,  # Only CC0 licensed music (completely free)
                'boost': 'popularity_total'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            audio_files = []
            
            for track in data.get('results', []):
                if track.get('audio'):
                    audio_files.append({
                        'id': f"jamendo_{track['id']}",
                        'title': track.get('name', 'Unknown Track'),
                        'url': track['audio'],
                        'duration': track.get('duration', 0),
                        'tags': ', '.join(track.get('tags', [])),
                        'source': 'jamendo',
                        'artist': track.get('artist_name', 'Unknown Artist')
                    })
            
            return audio_files
            
        except Exception as e:
            print(f"Error searching Jamendo audio: {e}")
            return []
    
    def _get_curated_audio(self, query: str, count: int) -> List[Dict]:
        """Get curated free music based on query"""
        themes = query.lower().split()
        
        # High-quality free music sources
        curated_tracks = {
            'calm': [
                {
                    'id': 'curated_calm_1',
                    'title': 'Peaceful Morning',
                    'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                    'duration': 30,
                    'tags': 'ambient, calm, peaceful',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_calm_2',
                    'title': 'Gentle Breeze',
                    'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                    'duration': 45,
                    'tags': 'soft, background, gentle',
                    'source': 'bensound',
                    'artist': 'Bensound'
                }
            ],
            'energetic': [
                {
                    'id': 'curated_energy_1',
                    'title': 'Dynamic Energy',
                    'url': 'https://www.bensound.com/bensound-music/bensound-energy.mp3',
                    'duration': 25,
                    'tags': 'energetic, upbeat, happy',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_energy_2',
                    'title': 'Funky Element',
                    'url': 'https://www.bensound.com/bensound-music/bensound-funkyelement.mp3',
                    'duration': 35,
                    'tags': 'joyful, melody, bright',
                    'source': 'bensound',
                    'artist': 'Bensound'
                }
            ],
            'romantic': [
                {
                    'id': 'curated_romantic_1',
                    'title': 'Sweet Romance',
                    'url': 'https://www.bensound.com/bensound-music/bensound-sweet.mp3',
                    'duration': 40,
                    'tags': 'romantic, piano, love',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_romantic_2',
                    'title': 'Creative Minds',
                    'url': 'https://www.bensound.com/bensound-music/bensound-creativeminds.mp3',
                    'duration': 32,
                    'tags': 'emotional, strings, heartfelt',
                    'source': 'bensound',
                    'artist': 'Bensound'
                }
            ],
            'default': [
                {
                    'id': 'curated_default_1',
                    'title': 'Summer Vibes',
                    'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                    'duration': 30,
                    'tags': 'ambient, calm, background',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_default_2',
                    'title': 'Acoustic Breeze',
                    'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                    'duration': 45,
                    'tags': 'piano, soft, emotional',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_default_3',
                    'title': 'Creative Minds',
                    'url': 'https://www.bensound.com/bensound-music/bensound-creativeminds.mp3',
                    'duration': 25,
                    'tags': 'gentle, melody, peaceful',
                    'source': 'bensound',
                    'artist': 'Bensound'
                }
            ]
        }
        
        # Determine which category to use
        if any(word in themes for word in ['calm', 'peaceful', 'ambient', 'soft', 'gentle']):
            category = 'calm'
        elif any(word in themes for word in ['energetic', 'upbeat', 'happy', 'joy', 'passion']):
            category = 'energetic'
        elif any(word in themes for word in ['romantic', 'love', 'heart', 'emotion']):
            category = 'romantic'
        else:
            category = 'default'
        
        tracks = curated_tracks.get(category, curated_tracks['default'])
        return random.sample(tracks, min(count, len(tracks)))
    
    def get_audio_by_theme(self, themes: List[str], mood: str) -> List[Dict]:
        """
        Get audio based on analyzed themes and mood
        """
        # Create search query from themes and mood
        search_terms = themes + [mood]
        query = ' '.join(search_terms)
        
        return self.search_audio(query, 5) 