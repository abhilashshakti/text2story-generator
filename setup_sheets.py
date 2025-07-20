#!/usr/bin/env python3
"""
Setup script for Google Sheets integration
This script helps you configure Google Sheets credentials for the text2story-generator
"""

import os
import json
from config import Config

def setup_sheets_credentials():
    """Setup Google Sheets credentials"""
    print("=== Google Sheets Setup ===")
    print()
    
    # Check if credentials are already set
    if Config.GOOGLE_SHEETS_CREDENTIALS:
        print("✅ Google Sheets credentials found in environment variable")
        print("The application should work with Google Sheets integration.")
        return True
    
    if os.path.exists('service-account.json'):
        print("✅ Google Sheets credentials found in service-account.json")
        print("The application should work with Google Sheets integration.")
        return True
    
    print("❌ No Google Sheets credentials found")
    print()
    print("To enable Google Sheets integration, you have two options:")
    print()
    print("Option 1: Environment Variable (Recommended for production)")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Google Sheets API")
    print("4. Create a Service Account")
    print("5. Download the JSON key file")
    print("6. Set the GOOGLE_SHEETS_CREDENTIALS environment variable with the JSON content")
    print()
    print("Option 2: Local File (For development)")
    print("1. Download your service account JSON file")
    print("2. Rename it to 'service-account.json'")
    print("3. Place it in the project root directory")
    print()
    print("Note: Without Google Sheets credentials, the application will still work")
    print("but the 'Save to Sheets' feature will be disabled.")
    print()
    
    return False

if __name__ == "__main__":
    setup_sheets_credentials() 