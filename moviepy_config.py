import os

# Force MoviePy to not use ImageMagick to avoid 'unset' error
# This ensures text clips always use the label method
os.environ['IMAGEMAGICK_BINARY'] = ''

print("MoviePy configured to use label method only (no ImageMagick)") 