import os

# Properly configure MoviePy to avoid ImageMagick issues in production
# Set ImageMagick binary to a non-existent path to force label method
os.environ['IMAGEMAGICK_BINARY'] = '/dev/null'

# Alternative: you can also try setting it to a dummy path
# os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/false'

print("MoviePy configured to use label method only (no ImageMagick)") 