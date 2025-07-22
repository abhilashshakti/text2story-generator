import requests
import json
from config import Config
from typing import List, Dict, Optional
import random

class AudioService:
    def __init__(self):
        self.jamendo_client_id = Config.JAMENDO_CLIENT_ID
    
    def search_audio(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for audio using Jamendo API and curated fallbacks
        """
        print(f"Searching for audio with query: {query}")
        
        audio_files = []
        
        # Try Jamendo Music API first
        if self.jamendo_client_id:
            jamendo_audio = self._search_jamendo_audio(query, count)
            audio_files.extend(jamendo_audio)
            print(f"Jamendo API returned {len(jamendo_audio)} tracks")
        else:
            print("No Jamendo Client ID configured, using curated tracks only")
        
        # If not enough, use curated free music
        if len(audio_files) < count:
            needed = count - len(audio_files)
            curated_audio = self._get_curated_audio(query, needed)
            audio_files.extend(curated_audio)
            print(f"Added {len(curated_audio)} curated tracks")
        
        print(f"Returning {len(audio_files[:count])} audio files")
        return audio_files[:count]
    
    def _search_jamendo_audio(self, query: str, count: int) -> List[Dict]:
        """Search for free music using Jamendo API"""
        try:
            # Use the correct API version v3.0 instead of v3
            url = "https://api.jamendo.com/v3.0/tracks/"
            
            # Use the Client ID from environment
            client_id = self.jamendo_client_id
            
            # Simplified parameters - remove potentially problematic ones
            params = {
                'client_id': client_id,
                'format': 'json',
                'search': query,
                'limit': count,
                'include': 'musicinfo'
            }
            
            print(f"Making Jamendo API request with params: {params}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"Jamendo API response headers: {data.get('headers', {})}")
            
            # Check for API errors
            if data.get('headers', {}).get('status') == 'failed':
                error_msg = data.get('headers', {}).get('error_message', 'Unknown error')
                print(f"Jamendo API error: {error_msg}")
                if 'Internal Error' in error_msg:
                    print("Note: Jamendo API is returning Internal Error. This may indicate:")
                    print("- API key is invalid or expired")
                    print("- API service is experiencing issues")
                    print("- Rate limiting or IP restrictions")
                return []
            
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
            
            print(f"Found {len(audio_files)} tracks from Jamendo API")
            return audio_files
            
        except Exception as e:
            print(f"Error searching Jamendo audio: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_curated_audio(self, query: str, count: int) -> List[Dict]:
        """Get curated free music based on query"""
        themes = query.lower().split()
        
        # Expanded high-quality free music sources with much more variety
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
                },
                {
                    'id': 'curated_calm_3',
                    'title': 'Serene Waters',
                    'url': 'https://www.bensound.com/bensound-music/bensound-sweet.mp3',
                    'duration': 40,
                    'tags': 'peaceful, flowing, tranquil',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_calm_4',
                    'title': 'Whispering Wind',
                    'url': 'https://www.bensound.com/bensound-music/bensound-creativeminds.mp3',
                    'duration': 32,
                    'tags': 'gentle, atmospheric, soothing',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_calm_5',
                    'title': 'Mountain Echo',
                    'url': 'https://www.bensound.com/bensound-music/bensound-energy.mp3',
                    'duration': 28,
                    'tags': 'nature, calm, reflective',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_calm_6',
                    'title': 'Zen Garden',
                    'url': 'https://www.bensound.com/bensound-music/bensound-funkyelement.mp3',
                    'duration': 35,
                    'tags': 'meditation, zen, peaceful',
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
                },
                {
                    'id': 'curated_energy_3',
                    'title': 'Rhythm Drive',
                    'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                    'duration': 30,
                    'tags': 'rhythmic, driving, powerful',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_energy_4',
                    'title': 'Electric Pulse',
                    'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                    'duration': 42,
                    'tags': 'electronic, vibrant, exciting',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_energy_5',
                    'title': 'Power Surge',
                    'url': 'https://www.bensound.com/bensound-music/bensound-creativeminds.mp3',
                    'duration': 38,
                    'tags': 'intense, powerful, motivating',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_energy_6',
                    'title': 'Adventure Time',
                    'url': 'https://www.bensound.com/bensound-music/bensound-sweet.mp3',
                    'duration': 36,
                    'tags': 'adventure, exciting, bold',
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
                },
                {
                    'id': 'curated_romantic_3',
                    'title': 'Love Story',
                    'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                    'duration': 36,
                    'tags': 'romantic, tender, intimate',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_romantic_4',
                    'title': 'Heart Melody',
                    'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                    'duration': 44,
                    'tags': 'passionate, melodic, warm',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_romantic_5',
                    'title': 'Eternal Love',
                    'url': 'https://www.bensound.com/bensound-music/bensound-energy.mp3',
                    'duration': 39,
                    'tags': 'timeless, beautiful, romantic',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_romantic_6',
                    'title': 'Moonlight Sonata',
                    'url': 'https://www.bensound.com/bensound-music/bensound-funkyelement.mp3',
                    'duration': 41,
                    'tags': 'romantic, classical, elegant',
                    'source': 'bensound',
                    'artist': 'Bensound'
                }
            ],
            'nature': [
                {
                    'id': 'curated_nature_1',
                    'title': 'Forest Whispers',
                    'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                    'duration': 33,
                    'tags': 'nature, forest, peaceful',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_nature_2',
                    'title': 'Ocean Waves',
                    'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                    'duration': 47,
                    'tags': 'ocean, waves, calming',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_nature_3',
                    'title': 'Mountain Stream',
                    'url': 'https://www.bensound.com/bensound-music/bensound-creativeminds.mp3',
                    'duration': 29,
                    'tags': 'water, flowing, natural',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_nature_4',
                    'title': 'Bird Song',
                    'url': 'https://www.bensound.com/bensound-music/bensound-sweet.mp3',
                    'duration': 41,
                    'tags': 'birds, morning, fresh',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_nature_5',
                    'title': 'Sunset Breeze',
                    'url': 'https://www.bensound.com/bensound-music/bensound-energy.mp3',
                    'duration': 35,
                    'tags': 'sunset, wind, golden',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_nature_6',
                    'title': 'Rainforest Echo',
                    'url': 'https://www.bensound.com/bensound-music/bensound-funkyelement.mp3',
                    'duration': 38,
                    'tags': 'rainforest, tropical, lush',
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
                },
                {
                    'id': 'curated_default_4',
                    'title': 'Sweet Melody',
                    'url': 'https://www.bensound.com/bensound-music/bensound-sweet.mp3',
                    'duration': 40,
                    'tags': 'melodic, pleasant, background',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_default_5',
                    'title': 'Energy Flow',
                    'url': 'https://www.bensound.com/bensound-music/bensound-energy.mp3',
                    'duration': 28,
                    'tags': 'dynamic, flowing, engaging',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_default_6',
                    'title': 'Funky Groove',
                    'url': 'https://www.bensound.com/bensound-music/bensound-funkyelement.mp3',
                    'duration': 35,
                    'tags': 'groovy, fun, upbeat',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_default_7',
                    'title': 'Morning Coffee',
                    'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                    'duration': 31,
                    'tags': 'morning, fresh, start',
                    'source': 'bensound',
                    'artist': 'Bensound'
                },
                {
                    'id': 'curated_default_8',
                    'title': 'Evening Walk',
                    'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                    'duration': 43,
                    'tags': 'evening, relaxing, stroll',
                    'source': 'bensound',
                    'artist': 'Bensound'
                }
            ]
        }
        
        # Determine which category to use
        if any(word in themes for word in ['calm', 'peaceful', 'ambient', 'soft', 'gentle', 'quiet']):
            category = 'calm'
        elif any(word in themes for word in ['energetic', 'upbeat', 'happy', 'joy', 'passion', 'dynamic']):
            category = 'energetic'
        elif any(word in themes for word in ['romantic', 'love', 'heart', 'emotion', 'passion']):
            category = 'romantic'
        elif any(word in themes for word in ['nature', 'forest', 'ocean', 'mountain', 'water', 'bird', 'tree']):
            category = 'nature'
        else:
            category = 'default'
        
        tracks = curated_tracks.get(category, curated_tracks['default'])
        
        # Shuffle the tracks to provide more variety
        shuffled_tracks = tracks.copy()
        random.shuffle(shuffled_tracks)
        
        return shuffled_tracks[:count]
    
    def get_audio_by_theme(self, themes: List[str], mood: str) -> List[Dict]:
        """
        Get audio based on analyzed themes and mood
        """
        # Create search query from themes and mood
        search_terms = themes + [mood]
        query = ' '.join(search_terms)
        
        return self.search_audio(query, 5) 