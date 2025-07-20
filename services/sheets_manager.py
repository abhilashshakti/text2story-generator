import gspread
from google.oauth2.service_account import Credentials
from config import Config
import json
from typing import List, Dict, Optional
from datetime import datetime

class SheetsManager:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = None
        self.client = None
        self._setup_credentials()
    
    def _setup_credentials(self):
        """Setup Google Sheets credentials"""
        try:
            if Config.GOOGLE_SHEETS_CREDENTIALS:
                # Load credentials from environment variable
                creds_dict = json.loads(Config.GOOGLE_SHEETS_CREDENTIALS)
                self.creds = Credentials.from_service_account_info(creds_dict, scopes=self.scope)
            else:
                # Try to load from service account file
                self.creds = Credentials.from_service_account_file(
                    'service-account.json', scopes=self.scope
                )
            
            self.client = gspread.authorize(self.creds)
        except Exception as e:
            print(f"Error setting up Google Sheets credentials: {e}")
            self.client = None
    
    def create_poem_sheet(self, sheet_name: str = "Poem Stories") -> Optional[str]:
        """Create a new Google Sheet for poem management"""
        if not self.client:
            return None
        
        try:
            # Create new spreadsheet
            spreadsheet = self.client.create(sheet_name)
            
            # Setup headers
            worksheet = spreadsheet.sheet1
            headers = [
                'Date', 'Poem Text', 'Themes', 'Mood', 'Video URL', 
                'Audio URL', 'Status', 'Generated File', 'Notes'
            ]
            worksheet.update('A1:I1', [headers])
            
            # Format headers
            worksheet.format('A1:I1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            return spreadsheet.url
            
        except Exception as e:
            print(f"Error creating poem sheet: {e}")
            return None
    
    def add_poem(self, poem_text: str, themes: List[str] = None, 
                 mood: str = None, video_url: str = None, 
                 audio_url: str = None, notes: str = None) -> bool:
        """Add a new poem to the sheet"""
        if not self.client:
            return False
        
        try:
            # Get the first worksheet
            worksheet = self.client.open("Poem Stories").sheet1
            
            # Prepare row data
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                poem_text,
                ', '.join(themes) if themes else '',
                mood or '',
                video_url or '',
                audio_url or '',
                'Pending',
                '',
                notes or ''
            ]
            
            # Append row
            worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            print(f"Error adding poem to sheet: {e}")
            return False
    
    def get_pending_poems(self) -> List[Dict]:
        """Get all poems with 'Pending' status"""
        if not self.client:
            return []
        
        try:
            worksheet = self.client.open("Poem Stories").sheet1
            all_records = worksheet.get_all_records()
            
            pending_poems = []
            for record in all_records:
                if record.get('Status', '').lower() == 'pending':
                    pending_poems.append(record)
            
            return pending_poems
            
        except Exception as e:
            print(f"Error getting pending poems: {e}")
            return []
    
    def update_poem_status(self, row_index: int, status: str, 
                          generated_file: str = None) -> bool:
        """Update the status of a poem"""
        if not self.client:
            return False
        
        try:
            worksheet = self.client.open("Poem Stories").sheet1
            
            # Update status (column G)
            worksheet.update(f'G{row_index + 2}', status)
            
            # Update generated file if provided (column H)
            if generated_file:
                worksheet.update(f'H{row_index + 2}', generated_file)
            
            return True
            
        except Exception as e:
            print(f"Error updating poem status: {e}")
            return False
    
    def get_all_poems(self) -> List[Dict]:
        """Get all poems from the sheet"""
        if not self.client:
            return []
        
        try:
            worksheet = self.client.open("Poem Stories").sheet1
            return worksheet.get_all_records()
            
        except Exception as e:
            print(f"Error getting all poems: {e}")
            return []
    
    def search_poems(self, query: str) -> List[Dict]:
        """Search poems by text content"""
        if not self.client:
            return []
        
        try:
            all_poems = self.get_all_poems()
            matching_poems = []
            
            for poem in all_poems:
                poem_text = poem.get('Poem Text', '').lower()
                themes = poem.get('Themes', '').lower()
                notes = poem.get('Notes', '').lower()
                
                if (query.lower() in poem_text or 
                    query.lower() in themes or 
                    query.lower() in notes):
                    matching_poems.append(poem)
            
            return matching_poems
            
        except Exception as e:
            print(f"Error searching poems: {e}")
            return []
    
    def export_to_csv(self, filename: str = "poems_export.csv") -> bool:
        """Export poems to CSV file"""
        if not self.client:
            return False
        
        try:
            worksheet = self.client.open("Poem Stories").sheet1
            all_records = worksheet.get_all_records()
            
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if all_records:
                    fieldnames = all_records[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_records)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False 