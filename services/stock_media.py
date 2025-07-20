import requests
import json
from config import Config
from typing import List, Dict, Optional

class StockMediaService:
    def __init__(self):
        self.pexels_api_key = Config.PEXELS_API_KEY
    
    def search_videos(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for stock videos using Pexels API
        """
        videos = []
        
        # Search Pexels for videos
        if self.pexels_api_key:
            pexels_videos = self._search_pexels_videos(query, count)
            videos.extend(pexels_videos)
        
        return videos[:count]
    
    def search_audio(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for stock audio - using curated free music
        """
        print(f"Searching for audio with query: {query}")
        
        # Get themed audio based on query
        audio_files = self._get_themed_audio(query, count)
        
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
    
    def _get_themed_audio(self, query: str, count: int) -> List[Dict]:
        """Get themed audio based on query"""
        themes = query.lower().split()
        
        # Use better free music sources
        if any(word in themes for word in ['calm', 'peaceful', 'ambient', 'soft', 'gentle']):
            audio_files = [
                {
                    'id': 'ambient_1',
                    'title': 'Peaceful Ambient',
                    'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                    'duration': 30,
                    'tags': 'ambient, calm, peaceful',
                    'source': 'bensound'
                },
                {
                    'id': 'ambient_2',
                    'title': 'Soft Background',
                    'url': 'https://www.bensound.com/bensound-music/bensound-creativeminds.mp3',
                    'duration': 45,
                    'tags': 'soft, background, gentle',
                    'source': 'bensound'
                }
            ]
        elif any(word in themes for word in ['energetic', 'upbeat', 'happy', 'joy', 'passion']):
            audio_files = [
                {
                    'id': 'energetic_1',
                    'title': 'Upbeat Energy',
                    'url': 'https://www.bensound.com/bensound-music/bensound-energy.mp3',
                    'duration': 25,
                    'tags': 'energetic, upbeat, happy',
                    'source': 'bensound'
                },
                {
                    'id': 'energetic_2',
                    'title': 'Joyful Melody',
                    'url': 'https://www.bensound.com/bensound-music/bensound-funkyelement.mp3',
                    'duration': 35,
                    'tags': 'joyful, melody, bright',
                    'source': 'bensound'
                }
            ]
        elif any(word in themes for word in ['romantic', 'love', 'heart', 'emotion']):
            audio_files = [
                {
                    'id': 'romantic_1',
                    'title': 'Romantic Piano',
                    'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                    'duration': 40,
                    'tags': 'romantic, piano, love',
                    'source': 'bensound'
                },
                {
                    'id': 'romantic_2',
                    'title': 'Emotional Strings',
                    'url': 'https://www.bensound.com/bensound-music/bensound-sweet.mp3',
                    'duration': 32,
                    'tags': 'emotional, strings, heartfelt',
                    'source': 'bensound'
                }
            ]
        else:
            # Default audio for any theme
            audio_files = self._get_default_audio()
        
        return audio_files[:count]
    
    def _get_default_audio(self) -> List[Dict]:
        """Return default audio options when API is not available"""
        return [
            {
                'id': 'default_1',
                'title': 'Ambient Background',
                'url': 'https://www.bensound.com/bensound-music/bensound-summer.mp3',
                'duration': 30,
                'tags': 'ambient, calm, background',
                'source': 'bensound'
            },
            {
                'id': 'default_2',
                'title': 'Soft Piano',
                'url': 'https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3',
                'duration': 45,
                'tags': 'piano, soft, emotional',
                'source': 'bensound'
            },
            {
                'id': 'default_3',
                'title': 'Gentle Melody',
                'url': 'https://www.bensound.com/bensound-music/bensound-creativeminds.mp3',
                'duration': 25,
                'tags': 'gentle, melody, peaceful',
                'source': 'bensound'
            },
            {
                'id': 'default_4',
                'title': 'Calm Atmosphere',
                'url': 'https://www.bensound.com/bensound-music/bensound-sweet.mp3',
                'duration': 40,
                'tags': 'calm, atmosphere, relaxing',
                'source': 'bensound'
            },
            {
                'id': 'default_5',
                'title': 'Peaceful Sounds',
                'url': 'https://www.bensound.com/bensound-music/bensound-energy.mp3',
                'duration': 35,
                'tags': 'peaceful, sounds, tranquil',
                'source': 'bensound'
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