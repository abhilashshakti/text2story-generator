import os
from moviepy.config import change_settings

# Detect the operating system and set appropriate ImageMagick path
def get_imagemagick_path():
    """Get the appropriate ImageMagick path based on the environment"""
    
    # Check if we're on Railway (Linux environment)
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.path.exists('/app'):
        # Railway/Linux paths
        possible_paths = [
            "/usr/bin/convert",  # Standard Linux path
            "/usr/local/bin/convert",  # Alternative Linux path
            "convert"  # Use system PATH
        ]
    else:
        # Local development (macOS)
        possible_paths = [
            "/opt/homebrew/bin/convert",  # Homebrew path
            "/usr/local/bin/convert",  # Alternative macOS path
            "convert"  # Use system PATH
        ]
    
    # Try to find a working ImageMagick installation
    for path in possible_paths:
        try:
            import subprocess
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"Found ImageMagick at: {path}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    # If no ImageMagick found, return None to use fallback
    print("Warning: ImageMagick not found, will use fallback text rendering")
    return None

# Get the appropriate ImageMagick path
IMAGEMAGICK_BINARY = get_imagemagick_path()

# Configure MoviePy
if IMAGEMAGICK_BINARY:
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})
    print(f"MoviePy configured to use ImageMagick at: {IMAGEMAGICK_BINARY}")
else:
    print("MoviePy will use fallback text rendering (no ImageMagick)") 