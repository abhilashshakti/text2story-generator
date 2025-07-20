#!/usr/bin/env python3
"""
Test script for audio integration
"""

import os
from dotenv import load_dotenv
from services.audio_service import AudioService

# Load environment variables
load_dotenv()

def test_audio_service():
    """Test the audio service with different queries"""
    print("🎵 Testing Audio Service...")
    
    # Initialize audio service
    audio_service = AudioService()
    
    # Test queries
    test_queries = [
        "peaceful ambient",
        "energetic upbeat", 
        "romantic piano",
        "nature sounds"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            audio_files = audio_service.search_audio(query, 3)
            print(f"   Found {len(audio_files)} audio files")
            
            for i, audio in enumerate(audio_files, 1):
                print(f"   {i}. {audio['title']} by {audio['artist']} ({audio['source']})")
                print(f"      Duration: {audio['duration']}s")
                print(f"      URL: {audio['url'][:50]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Audio service test completed!")

if __name__ == "__main__":
    test_audio_service() 