import os
from moviepy.config import change_settings

# Set ImageMagick path for macOS (installed via Homebrew)
IMAGEMAGICK_BINARY = "/opt/homebrew/bin/convert"

# Configure MoviePy to use ImageMagick
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

print(f"MoviePy configured to use ImageMagick at: {IMAGEMAGICK_BINARY}") 