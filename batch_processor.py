#!/usr/bin/env python3
"""
Batch Processor for Text2Story Generator
Processes multiple poems from Google Sheets automatically
"""

import os
import sys
import time
import json
from datetime import datetime
from services.sheets_manager import SheetsManager
from services.theme_analyzer import ThemeAnalyzer
from services.stock_media import StockMediaService
from services.audio_service import AudioService
from app import create_story_video
from config import Config
import uuid

class BatchProcessor:
    def __init__(self):
        self.sheets_manager = SheetsManager()
        self.theme_analyzer = ThemeAnalyzer()
        self.stock_media = StockMediaService()
        self.audio_service = AudioService()
        
    def process_pending_poems(self, max_poems=10):
        """Process all pending poems from Google Sheets"""
        print("🔄 Starting batch processing...")
        
        # Get pending poems
        pending_poems = self.sheets_manager.get_pending_poems()
        
        if not pending_poems:
            print("✅ No pending poems found")
            return
        
        print(f"📝 Found {len(pending_poems)} pending poems")
        
        # Limit processing
        poems_to_process = pending_poems[:max_poems]
        
        successful = 0
        failed = 0
        
        for i, poem in enumerate(poems_to_process, 1):
            print(f"\n📖 Processing poem {i}/{len(poems_to_process)}")
            print(f"   Text: {poem['Poem Text'][:50]}...")
            
            try:
                # Analyze theme
                theme_analysis = self.theme_analyzer.analyze_poem_theme(poem['Poem Text'])
                
                # Get suggested media
                suggested_videos = self.stock_media.get_video_by_theme(
                    theme_analysis.get('themes', []), 
                    theme_analysis.get('mood', '')
                )
                
                suggested_audio = self.audio_service.get_audio_by_theme(
                    theme_analysis.get('themes', []), 
                    theme_analysis.get('mood', '')
                )
                
                # Select first available video and audio
                video_url = suggested_videos[0]['url'] if suggested_videos else ''
                audio_url = suggested_audio[0]['url'] if suggested_audio else ''
                
                # Generate story
                output_filename = f"batch_story_{uuid.uuid4().hex[:8]}.mp4"
                output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
                
                success = create_story_video(
                    poem['Poem Text'],
                    video_url,
                    audio_url,
                    Config.DEFAULT_FONT_SIZE,
                    Config.DEFAULT_TEXT_COLOR,
                    Config.DEFAULT_VIDEO_DURATION,
                    output_path
                )
                
                if success:
                    # Update sheet status
                    self.sheets_manager.update_poem_status(
                        pending_poems.index(poem),
                        'Completed',
                        output_filename
                    )
                    
                    print(f"   ✅ Generated: {output_filename}")
                    successful += 1
                else:
                    # Update sheet status
                    self.sheets_manager.update_poem_status(
                        pending_poems.index(poem),
                        'Failed'
                    )
                    
                    print(f"   ❌ Failed to generate story")
                    failed += 1
                
                # Add delay to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                failed += 1
                
                # Update sheet status
                try:
                    self.sheets_manager.update_poem_status(
                        pending_poems.index(poem),
                        'Failed'
                    )
                except:
                    pass
        
        print(f"\n🎉 Batch processing completed!")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        
    def process_specific_poems(self, poem_ids):
        """Process specific poems by ID"""
        print(f"🔄 Processing {len(poem_ids)} specific poems...")
        
        all_poems = self.sheets_manager.get_all_poems()
        poems_to_process = [p for p in all_poems if p.get('id') in poem_ids]
        
        if not poems_to_process:
            print("❌ No poems found with specified IDs")
            return
        
        # Process each poem
        for poem in poems_to_process:
            print(f"\n📖 Processing poem: {poem['Poem Text'][:50]}...")
            # Similar processing logic as above
            # (Implementation would be similar to process_pending_poems)
    
    def export_results(self, filename=None):
        """Export processing results to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_results_{timestamp}.csv"
        
        success = self.sheets_manager.export_to_csv(filename)
        
        if success:
            print(f"📊 Results exported to {filename}")
        else:
            print("❌ Failed to export results")
    
    def get_processing_stats(self):
        """Get processing statistics"""
        all_poems = self.sheets_manager.get_all_poems()
        
        stats = {
            'total': len(all_poems),
            'pending': len([p for p in all_poems if p.get('Status') == 'Pending']),
            'completed': len([p for p in all_poems if p.get('Status') == 'Completed']),
            'failed': len([p for p in all_poems if p.get('Status') == 'Failed'])
        }
        
        return stats

def main():
    """Main function for command-line usage"""
    processor = BatchProcessor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python batch_processor.py pending [max_poems]")
        print("  python batch_processor.py stats")
        print("  python batch_processor.py export [filename]")
        return
    
    command = sys.argv[1]
    
    if command == "pending":
        max_poems = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        processor.process_pending_poems(max_poems)
    
    elif command == "stats":
        stats = processor.get_processing_stats()
        print("\n📊 Processing Statistics:")
        print(f"   Total poems: {stats['total']}")
        print(f"   Pending: {stats['pending']}")
        print(f"   Completed: {stats['completed']}")
        print(f"   Failed: {stats['failed']}")
    
    elif command == "export":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        processor.export_results(filename)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main() 