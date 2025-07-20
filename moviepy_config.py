import os

# Configure ImageMagick for high-quality text rendering in production
# Only disable it if we detect issues, otherwise allow for better text quality

def configure_moviepy_with_imagemagick():
    """Configure MoviePy to use ImageMagick when available for better text quality"""
    try:
        # Try to find ImageMagick binary (Railway typically has this)
        import shutil
        magick_binary = shutil.which('magick') or shutil.which('convert')
        
        if magick_binary:
            print(f"✅ Found ImageMagick at: {magick_binary}")
            
            # Set the binary path for MoviePy
            os.environ['IMAGEMAGICK_BINARY'] = magick_binary
            
            # Configure MoviePy
            try:
                import moviepy.config as mpconfig
                mpconfig.IMAGEMAGICK_BINARY = magick_binary
                print("✅ ImageMagick configured for MoviePy text rendering")
                
                # Test ImageMagick quickly
                import subprocess
                result = subprocess.run([magick_binary, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ ImageMagick test successful: {result.stdout.split()[0:3]}")
                    return True
                else:
                    print(f"⚠️ ImageMagick test failed: {result.stderr}")
                    
            except Exception as config_error:
                print(f"⚠️ MoviePy configuration error: {config_error}")
        else:
            print("ℹ️ ImageMagick not found in PATH, will use PIL fallback")
            
        return False
        
    except Exception as e:
        print(f"❌ Error configuring ImageMagick: {e}")
        # Disable ImageMagick on error to avoid crashes
        os.environ['IMAGEMAGICK_BINARY'] = ''
        try:
            import moviepy.config as mpconfig
            mpconfig.IMAGEMAGICK_BINARY = ''
        except:
            pass
        return False

# Configure on import
imagemagick_available = configure_moviepy_with_imagemagick()
print(f"MoviePy configured - ImageMagick available: {imagemagick_available}") 