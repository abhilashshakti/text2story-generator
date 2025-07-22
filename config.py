import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Pexels API
    PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
    
    # Jamendo Music API (for free music)
    JAMENDO_CLIENT_ID = os.environ.get('JAMENDO_CLIENT_ID')
    
    # Google Sheets API
    GOOGLE_SHEETS_CREDENTIALS = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    
    # Instagram Graph API (for future auto-posting)
    INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    # File paths
    UPLOAD_FOLDER = 'uploads'
    TEMP_FOLDER = 'temp'
    
    # Video settings
    DEFAULT_VIDEO_DURATION = 15  # seconds
    DEFAULT_FONT_SIZE = 80  # Increased for better readability
    DEFAULT_TEXT_COLOR = '#FFFFFF'
    
    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']
    
    # Supported audio formats
    SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.aac'] 