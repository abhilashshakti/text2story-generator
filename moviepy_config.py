import os

# Multiple approaches to disable ImageMagick completely
os.environ['IMAGEMAGICK_BINARY'] = ''
os.environ['IMAGEIO_FFMPEG_EXE'] = ''

# Try to import and configure moviepy directly
try:
    import moviepy.config as mpconfig
    mpconfig.IMAGEMAGICK_BINARY = ''
except:
    pass

print("MoviePy configured to avoid ImageMagick completely") 