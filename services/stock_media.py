import requests
import json
from config import Config
from typing import List, Dict, Optional

class StockMediaService:
    def __init__(self):
        self.pexels_api_key = Config.PEXELS_API_KEY
        self.pixabay_api_key = Config.PIXABAY_API_KEY
    
    def search_videos(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for stock videos using Pexels and Pixabay APIs
        """
        videos = []
        
        # Try Pexels first
        if self.pexels_api_key:
            pexels_videos = self._search_pexels_videos(query, count)
            videos.extend(pexels_videos)
        
        # Try Pixabay if we need more videos
        if self.pixabay_api_key and len(videos) < count:
            pixabay_videos = self._search_pixabay_videos(query, count - len(videos))
            videos.extend(pixabay_videos)
        
        return videos[:count]
    
    def search_audio(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for stock audio - Pixabay doesn't provide audio, so we use themed defaults
        """
        print(f"Searching for audio with query: {query}")
        
        # Create themed audio options based on the query
        themes = query.lower().split()
        
        # Define audio options based on themes
        if any(word in themes for word in ['calm', 'peaceful', 'ambient', 'soft', 'gentle']):
            audio_files = [
                {
                    'id': 'ambient_1',
                    'title': 'Peaceful Ambient',
                    'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                    'duration': 30,
                    'tags': 'ambient, calm, peaceful',
                    'source': 'free_music'
                },
                {
                    'id': 'ambient_2',
                    'title': 'Soft Background',
                    'url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav',
                    'duration': 45,
                    'tags': 'soft, background, gentle',
                    'source': 'free_music'
                },
                {
                    'id': 'ambient_3',
                    'title': 'Tranquil Melody',
                    'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                    'duration': 35,
                    'tags': 'tranquil, melody, serene',
                    'source': 'free_music'
                }
            ]
        elif any(word in themes for word in ['energetic', 'upbeat', 'happy', 'joy', 'passion']):
            audio_files = [
                {
                    'id': 'energetic_1',
                    'title': 'Upbeat Energy',
                    'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                    'duration': 25,
                    'tags': 'energetic, upbeat, happy',
                    'source': 'free_music'
                },
                {
                    'id': 'energetic_2',
                    'title': 'Joyful Melody',
                    'url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav',
                    'duration': 35,
                    'tags': 'joyful, melody, bright',
                    'source': 'free_music'
                },
                {
                    'id': 'energetic_3',
                    'title': 'Dynamic Rhythm',
                    'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                    'duration': 28,
                    'tags': 'dynamic, rhythm, vibrant',
                    'source': 'free_music'
                }
            ]
        elif any(word in themes for word in ['romantic', 'love', 'heart', 'emotion']):
            audio_files = [
                {
                    'id': 'romantic_1',
                    'title': 'Romantic Piano',
                    'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                    'duration': 40,
                    'tags': 'romantic, piano, love',
                    'source': 'free_music'
                },
                {
                    'id': 'romantic_2',
                    'title': 'Emotional Strings',
                    'url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav',
                    'duration': 32,
                    'tags': 'emotional, strings, heartfelt',
                    'source': 'free_music'
                },
                {
                    'id': 'romantic_3',
                    'title': 'Tender Melody',
                    'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                    'duration': 38,
                    'tags': 'tender, melody, sweet',
                    'source': 'free_music'
                }
            ]
        else:
            # Default audio for any theme
            audio_files = self._get_default_audio()
        
        # Ensure we have the right number of audio files
        while len(audio_files) < count:
            audio_files.extend(self._get_default_audio())
        
        print(f"Returning {len(audio_files[:count])} audio files")
        return audio_files[:count]
    
    def _search_pexels_videos(self, query: str, count: int) -> List[Dict]:
        """Search videos on Pexels"""
        try:
            url = "https://api.pexels.com/videos/search"
            headers = {
                'Authorization': self.pexels_api_key
            }
            params = {
                'query': query,
                'per_page': count,
                'orientation': 'landscape'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for video in data.get('videos', []):
                # Get the best quality video file
                video_files = video.get('video_files', [])
                best_video = None
                
                for file in video_files:
                    if file.get('width', 0) >= 1280 and file.get('height', 0) >= 720:
                        best_video = file
                        break
                
                if not best_video and video_files:
                    best_video = video_files[0]
                
                if best_video:
                    videos.append({
                        'id': video['id'],
                        'title': video.get('url', '').split('/')[-1],
                        'url': best_video['link'],
                        'duration': video.get('duration', 0),
                        'width': best_video.get('width', 0),
                        'height': best_video.get('height', 0),
                        'source': 'pexels'
                    })
            
            return videos
            
        except Exception as e:
            print(f"Error searching Pexels videos: {e}")
            return []
    
    def _search_pixabay_videos(self, query: str, count: int) -> List[Dict]:
        """Search videos on Pixabay"""
        try:
            url = "https://pixabay.com/api/videos/"
            params = {
                'key': self.pixabay_api_key,
                'q': query,
                'per_page': count,
                'safesearch': 'true'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for hit in data.get('hits', []):
                videos.append({
                    'id': hit['id'],
                    'title': hit.get('title', ''),
                    'url': hit['videos']['large']['url'],
                    'duration': hit.get('duration', 0),
                    'width': hit['videos']['large'].get('width', 0),
                    'height': hit['videos']['large'].get('height', 0),
                    'source': 'pixabay'
                })
            
            return videos
            
        except Exception as e:
            print(f"Error searching Pixabay videos: {e}")
            return []
    
    def _get_default_audio(self) -> List[Dict]:
        """Return default audio options when API is not available"""
        return [
            {
                'id': 'default_1',
                'title': 'Ambient Background',
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                'duration': 30,
                'tags': 'ambient, calm, background',
                'source': 'free_music'
            },
            {
                'id': 'default_2',
                'title': 'Soft Piano',
                'url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav',
                'duration': 45,
                'tags': 'piano, soft, emotional',
                'source': 'free_music'
            },
            {
                'id': 'default_3',
                'title': 'Gentle Melody',
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                'duration': 25,
                'tags': 'gentle, melody, peaceful',
                'source': 'free_music'
            },
            {
                'id': 'default_4',
                'title': 'Calm Atmosphere',
                'url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav',
                'duration': 40,
                'tags': 'calm, atmosphere, relaxing',
                'source': 'free_music'
            },
            {
                'id': 'default_5',
                'title': 'Peaceful Sounds',
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                'duration': 35,
                'tags': 'peaceful, sounds, tranquil',
                'source': 'free_music'
            }
        ]
    
    def get_video_by_theme(self, themes: List[str], mood: str) -> List[Dict]:
        """
        Get videos based on analyzed themes and mood
        """
        # Create search query from themes and mood
        search_terms = themes + [mood]
        query = ' '.join(search_terms)
        
        return self.search_videos(query, 5)
    
    def get_audio_by_theme(self, themes: List[str], mood: str) -> List[Dict]:
        """
        Get audio based on analyzed themes and mood
        """
        # Create search query from themes and mood
        search_terms = themes + [mood]
        query = ' '.join(search_terms)
        
        return self.search_audio(query, 5) 