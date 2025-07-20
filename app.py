from flask import Flask, render_template, request, jsonify, send_file, Response
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import os
import requests
import tempfile
import uuid
import numpy as np
from werkzeug.utils import secure_filename
import json
from config import Config

# Configure MoviePy with ImageMagick
import moviepy_config

# Import our services
from services.theme_analyzer import ThemeAnalyzer
from services.stock_media import StockMediaService
from services.audio_service import AudioService
from services.sheets_manager import SheetsManager

app = Flask(__name__)
app.config.from_object(Config)

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Initialize services
theme_analyzer = ThemeAnalyzer()
stock_media = StockMediaService()
audio_service = AudioService()
sheets_manager = SheetsManager()

# Clean up old temporary files on startup
def cleanup_old_temp_files():
    """Clean up temporary files older than 1 hour"""
    try:
        temp_dir = app.config['TEMP_FOLDER']
        current_time = time.time()
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                # Remove files older than 1 hour
                if current_time - os.path.getmtime(file_path) > 3600:
                    try:
                        os.unlink(file_path)
                        print(f"Cleaned up old temp file: {filename}")
                    except Exception as e:
                        print(f"Could not clean up {filename}: {e}")
    except Exception as e:
        print(f"Error during temp file cleanup: {e}")

# Import time module for cleanup
import time

def get_available_fonts():
    """Detect available fonts with bundled high-quality fonts prioritized"""
    available_fonts = []
    
    print("🔍 Starting font detection with bundled fonts...")
    
    # PRIORITY 1: Our bundled high-quality fonts (guaranteed to exist)
    bundled_fonts = [
        os.path.join('static', 'fonts', 'Roboto-Bold.ttf'),
        os.path.join('static', 'fonts', 'Roboto-Regular.ttf')
    ]
    
    for font_path in bundled_fonts:
        if os.path.exists(font_path):
            available_fonts.append(font_path)
            print(f"✅ Found bundled font: {font_path}")
        else:
            print(f"❌ Missing bundled font: {font_path}")
    
    # PRIORITY 2: System fonts (if any exist in Railway)
    font_directories = [
        '/usr/share/fonts',
        '/usr/local/share/fonts',
        '/usr/share/fonts/truetype',
        '/usr/share/fonts/TTF',
        '/usr/share/fonts/opentype',
        '/usr/share/fonts/Type1',
        '/System/Library/Fonts',  # macOS
        '/Library/Fonts',         # macOS
    ]
    
    existing_dirs = []
    for font_dir in font_directories:
        if os.path.exists(font_dir):
            existing_dirs.append(font_dir)
            print(f"📁 Found system font directory: {font_dir}")
    
    # Simple recursive search for TTF/OTF files
    import glob
    
    for font_dir in existing_dirs:
        try:
            ttf_pattern = os.path.join(font_dir, "**", "*.ttf")
            ttf_files = glob.glob(ttf_pattern, recursive=True)
            
            otf_pattern = os.path.join(font_dir, "**", "*.otf") 
            otf_files = glob.glob(otf_pattern, recursive=True)
            
            all_fonts = ttf_files + otf_files
            
            # Prioritize common high-quality fonts
            priority_fonts = []
            regular_fonts = []
            
            for font_file in all_fonts:
                font_name = os.path.basename(font_file).lower()
                if any(keyword in font_name for keyword in ['dejavu', 'liberation', 'ubuntu', 'roboto', 'opensans']):
                    priority_fonts.append(font_file)
                else:
                    regular_fonts.append(font_file)
            
            # Add system fonts (avoiding duplicates)
            for font_file in priority_fonts + regular_fonts:
                if font_file not in available_fonts:
                    available_fonts.append(font_file)
                    if len(available_fonts) >= 15:  # Limit total fonts
                        break
                        
        except Exception as e:
            print(f"❌ Error scanning {font_dir}: {e}")
            continue
    
    print(f"🔍 Found {len(available_fonts)} total fonts:")
    for i, font in enumerate(available_fonts[:8]):
        print(f"   {i+1}. {os.path.basename(font)}")
    
    if len(available_fonts) > 8:
        print(f"   ... and {len(available_fonts) - 8} more")
    
    return available_fonts

@app.route('/')
def index():
    # Clean up old temp files on each request to homepage
    cleanup_old_temp_files()
    return render_template('index.html')

@app.route('/analyze-poem', methods=['POST'])
def analyze_poem():
    """Analyze poem and suggest themes, videos, and audio"""
    try:
        data = request.get_json()
        poem_text = data.get('poem_text', '')
        
        if not poem_text:
            return jsonify({'error': 'Poem text is required'}), 400
        
        # Analyze poem theme
        theme_analysis = theme_analyzer.analyze_poem_theme(poem_text)
        
        # Get suggested videos and audio based on analysis
        suggested_videos = stock_media.get_video_by_theme(
            theme_analysis.get('themes', []), 
            theme_analysis.get('mood', '')
        )
        
        suggested_audio = audio_service.get_audio_by_theme(
            theme_analysis.get('themes', []), 
            theme_analysis.get('mood', '')
        )
        
        return jsonify({
            'success': True,
            'theme_analysis': theme_analysis,
            'suggested_videos': suggested_videos,
            'suggested_audio': suggested_audio
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-story', methods=['POST'])
def generate_story():
    """Generate Instagram story with poem overlay"""
    try:
        data = request.get_json()
        poem_text = data.get('poem_text', '')
        video_url = data.get('video_url', '')
        audio_url = data.get('audio_url', '')
        font_size = data.get('font_size', app.config['DEFAULT_FONT_SIZE'])
        text_color = data.get('text_color', app.config['DEFAULT_TEXT_COLOR'])
        duration = data.get('duration', app.config['DEFAULT_VIDEO_DURATION'])
        save_to_sheets = data.get('save_to_sheets', False)
        
        if not poem_text:
            return jsonify({'error': 'Poem text is required'}), 400
        
        # Generate unique filename and use temp directory
        output_filename = f"story_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(app.config['TEMP_FOLDER'], output_filename)
        
        # Create the story video
        success = create_story_video(
            poem_text, video_url, audio_url, 
            font_size, text_color, duration, output_path
        )
        
        if success:
            # Save to Google Sheets if requested
            if save_to_sheets:
                try:
                    theme_analysis = theme_analyzer.analyze_poem_theme(poem_text)
                    sheets_manager.add_poem(
                        poem_text=poem_text,
                        themes=theme_analysis.get('themes', []),
                        mood=theme_analysis.get('mood', ''),
                        video_url=video_url,
                        audio_url=audio_url,
                        notes=f"Generated: {output_filename}"
                    )
                except Exception as e:
                    print(f"Error saving to sheets: {e}")
            
            # Get file size for user feedback
            file_path = os.path.join(app.config['TEMP_FOLDER'], output_filename)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            file_size_mb = round(file_size / (1024 * 1024), 1)
            
            return jsonify({
                'success': True,
                'output_file': output_filename,
                'file_size_mb': file_size_mb,
                'message': 'Story generated successfully!'
            })
        else:
            return jsonify({'error': 'Failed to generate story'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated story file and clean up after download"""
    try:
        file_path = os.path.join(app.config['TEMP_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get file size for logging
        file_size = os.path.getsize(file_path)
        print(f"Downloading file: {filename} ({file_size} bytes)")
        
        # Create a response that will clean up the file after sending
        def generate_and_cleanup():
            try:
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            finally:
                # Clean up the file after sending
                try:
                    os.unlink(file_path)
                    print(f"Cleaned up temporary file: {filename}")
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up {filename}: {cleanup_error}")
        
        return Response(
            generate_and_cleanup(),
            content_type='video/mp4',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': str(file_size)
            }
        )
    except Exception as e:
        print(f"Error downloading file {filename}: {e}")
        return jsonify({'error': str(e)}), 404

@app.route('/test-text-rendering')
def test_text_rendering():
    """Test endpoint to verify text rendering works in production"""
    try:
        # Test both MoviePy and PIL text rendering
        test_text = "Test overlay quality"
        video_width, video_height = 1080, 1920
        font_size = 60
        text_color = "#FFFFFF"
        duration = 5
        
        print("🧪 Testing text rendering capabilities...")
        
        # Test MoviePy TextClip
        moviepy_success = False
        try:
            text_clip = create_text_clip_with_moviepy(test_text, video_width, video_height, font_size, text_color, duration)
            if text_clip:
                moviepy_success = True
                text_clip.close()  # Clean up
        except Exception as e:
            print(f"MoviePy test failed: {e}")
        
        # Test enhanced PIL
        pil_success = False
        try:
            text_clip = create_enhanced_pil_text_clip(test_text, video_width, video_height, font_size, text_color, duration)
            if text_clip:
                pil_success = True
                text_clip.close()  # Clean up
        except Exception as e:
            print(f"Enhanced PIL test failed: {e}")
        
        # Check ImageMagick availability
        imagemagick_available = False
        try:
            import shutil
            magick_binary = shutil.which('magick') or shutil.which('convert')
            imagemagick_available = magick_binary is not None
        except:
            pass
        
        # Check available fonts using the detection function
        available_fonts = get_available_fonts()
        
        return jsonify({
            'status': 'success',
            'moviepy_rendering': moviepy_success,
            'enhanced_pil_rendering': pil_success,
            'imagemagick_available': imagemagick_available,
            'available_fonts': available_fonts,
            'environment': 'production' if os.environ.get('PORT') else 'development',
            'platform': os.name
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/test-text-image')
def test_text_image():
    """Test endpoint to generate a standalone text image for debugging"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Test parameters
        test_text = "Don't bend;\ndon't water it down;\ndon't try to make it logical"
        width, height = 1080, 1920
        font_size = 60
        text_color = "#FFFFFF"
        
        print(f"🧪 Testing text image generation: '{test_text}'")
        
        # Create image with black background
        img = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts
        available_fonts = get_available_fonts()
        font = None
        
        if available_fonts:
            for font_path in available_fonts[:3]:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"✅ Using font: {os.path.basename(font_path)}")
                    break
                except Exception as e:
                    print(f"❌ Failed font {font_path}: {e}")
                    continue
        
        if font is None:
            print("⚠️ Using default font")
            font = ImageFont.load_default()
        
        # Parse color
        if text_color.startswith('#'):
            text_color = text_color.lstrip('#')
            color_rgb = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            color_rgb = (255, 255, 255)
        
        # Draw text with outline
        lines = test_text.split('\n')
        line_height = font_size + 10
        total_height = len(lines) * line_height
        start_y = (height - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Black outline
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
            
            # White text
            draw.text((x, y), line, font=font, fill=color_rgb)
            print(f"✅ Drew line: '{line}' at ({x}, {y})")
        
        # Save test image
        test_path = os.path.join('temp', 'test_text_image.png')
        os.makedirs('temp', exist_ok=True)
        img.save(test_path)
        
        print(f"✅ Saved test image to {test_path}")
        
        # Return the image
        return send_file(test_path, mimetype='image/png')
        
    except Exception as e:
        print(f"❌ Error in test text image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/proxy-media')
def proxy_media():
    """Proxy media URLs to handle CORS and authentication issues"""
    url = request.args.get('url')
    media_type = request.args.get('type', 'video')  # video or audio
    
    print(f"Proxy request received: {url} (type: {media_type})")
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Add specific headers for different sources
        if 'pexels.com' in url:
            headers['Authorization'] = Config.PEXELS_API_KEY
            print(f"Proxying Pexels video with auth header: {url}")
        else:
            print(f"Proxying media without auth: {url}")
        
        response = requests.get(url, headers=headers, stream=True)
        print(f"Proxy response status: {response.status_code}")
        response.raise_for_status()
        
        # Stream the response
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk
        
        content_type = response.headers.get('content-type', 'video/mp4' if media_type == 'video' else 'audio/mpeg')
        print(f"Content type: {content_type}")
        
        return Response(
            generate(),
            content_type=content_type,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        print(f"Error proxying media: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to load media'}), 500

@app.route('/test-proxy')
def test_proxy():
    """Test endpoint to check if proxy is working"""
    return jsonify({'status': 'Proxy endpoint is working'})

@app.route('/cleanup-temp', methods=['POST'])
def cleanup_temp_files():
    """Manually clean up temporary files"""
    try:
        cleanup_old_temp_files()
        return jsonify({
            'success': True,
            'message': 'Temporary files cleaned up successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search-media', methods=['POST'])
def search_media():
    """Search for stock videos and audio"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        media_type = data.get('type', 'video')  # 'video' or 'audio'
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        if media_type == 'video':
            results = stock_media.search_videos(query, 10)
        else:
            results = audio_service.search_audio(query, 10)
        
        return jsonify({
            'success': True,
            'results': results,
            'type': media_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sheets/create', methods=['POST'])
def create_sheets():
    """Create a new Google Sheet for poem management"""
    try:
        data = request.get_json()
        sheet_name = data.get('sheet_name', 'Poem Stories')
        
        sheet_url = sheets_manager.create_poem_sheet(sheet_name)
        
        if sheet_url:
            return jsonify({
                'success': True,
                'sheet_url': sheet_url,
                'message': 'Google Sheet created successfully!'
            })
        else:
            return jsonify({'error': 'Failed to create Google Sheet'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sheets/poems')
def get_poems():
    """Get all poems from Google Sheets"""
    try:
        poems = sheets_manager.get_all_poems()
        return jsonify({
            'success': True,
            'poems': poems
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sheets/pending')
def get_pending_poems():
    """Get pending poems from Google Sheets"""
    try:
        pending_poems = sheets_manager.get_pending_poems()
        return jsonify({
            'success': True,
            'poems': pending_poems
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sheets/search', methods=['POST'])
def search_poems():
    """Search poems in Google Sheets"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = sheets_manager.search_poems(query)
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug-fonts')
def debug_fonts():
    """Debug endpoint to see what's available in Railway's container"""
    try:
        import glob
        
        debug_info = {
            "environment": "production" if os.environ.get('PORT') else 'development',
            "platform": os.name,
            "available_directories": [],
            "font_files_found": [],
            "all_usr_share_contents": [],
            "font_search_results": {}
        }
        
        # Check common directories
        check_dirs = [
            '/usr/share/fonts',
            '/usr/local/share/fonts', 
            '/usr/share/fonts/truetype',
            '/usr/share/fonts/TTF',
            '/usr/share',
            '/usr',
            '/opt',
            '/var',
            '/etc'
        ]
        
        for dir_path in check_dirs:
            if os.path.exists(dir_path):
                debug_info["available_directories"].append(dir_path)
                
                # If it's /usr/share, list its contents
                if dir_path == '/usr/share':
                    try:
                        contents = os.listdir(dir_path)
                        debug_info["all_usr_share_contents"] = sorted(contents)
                    except:
                        pass
        
        # Try to find ANY font files in the system
        search_patterns = [
            '/usr/**/*.ttf',
            '/usr/**/*.otf', 
            '/opt/**/*.ttf',
            '/var/**/*.ttf',
            '/**/*.ttf'  # Last resort - search everywhere (might be slow)
        ]
        
        for pattern in search_patterns:
            try:
                matches = glob.glob(pattern, recursive=True)
                debug_info["font_search_results"][pattern] = matches[:10]  # Limit results
            except Exception as e:
                debug_info["font_search_results"][pattern] = f"Error: {str(e)}"
        
        # Use our font detection function
        detected_fonts = get_available_fonts()
        debug_info["detected_fonts"] = detected_fonts
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_text_clip_with_pil(text, video_width, video_height, font_size, text_color, duration):
    """Create a text clip using PIL instead of MoviePy's TextClip to avoid ImageMagick issues"""
    try:
        from moviepy.video.VideoClip import ImageClip
        import textwrap
        
        # Debug: Log input parameters
        print(f"Creating text clip: text='{text[:50]}...', size={video_width}x{video_height}, font_size={font_size}, color={text_color}")
        
        # Ensure text is properly formatted
        if not text or not text.strip():
            print("Warning: Empty or whitespace-only text provided")
            text = "No text provided"
        
        # Normalize text - ensure consistent line breaks and spacing
        text = text.strip()
        # Replace multiple spaces with single space
        import re
        text = re.sub(r'\s+', ' ', text)
        print(f"Normalized text: '{text[:100]}...'")
        
        # Parse color - handle hex colors like '#ffffff' or named colors like 'white'
        if text_color.startswith('#'):
            # Convert hex to RGB
            text_color = text_color.lstrip('#')
            color_rgb = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            # Named colors - convert to RGB
            color_map = {
                'white': (255, 255, 255),
                'black': (0, 0, 0),
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'yellow': (255, 255, 0),
                'cyan': (0, 255, 255),
                'magenta': (255, 0, 255)
            }
            color_rgb = color_map.get(text_color.lower(), (255, 255, 255))
        
        # Calculate text area dimensions (90% of video width, allow for height)
        text_width = int(video_width * 0.9)
        text_height = int(video_height * 0.8)
        
        # Create image with transparent background
        img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font, fallback to default
        try:
            # Try common system fonts in order of preference
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                '/System/Library/Fonts/Arial.ttf',  # macOS
                '/System/Library/Fonts/Helvetica.ttc',  # macOS
                '/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf',  # Ubuntu
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux fallback
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Linux
            ]
            
            font = None
            used_font_path = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                        used_font_path = font_path
                        print(f"Using font: {font_path}")
                        break
                    except Exception as e:
                        print(f"Failed to load font {font_path}: {e}")
                        continue
            
            if font is None:
                # Create a more robust fallback font
                try:
                    # Try to create a basic font with consistent metrics
                    font = ImageFont.load_default()
                    used_font_path = "default"
                    print("Using default font - truetype fonts not found")
                    # Keep font size consistent across environments - no scaling
                except Exception as e:
                    print(f"Error loading default font: {e}")
                    # Create a minimal fallback
                    font = ImageFont.load_default()
                    used_font_path = "default_fallback"
                
        except Exception as font_error:
            print(f"Font loading error: {font_error}")
            font = ImageFont.load_default()
            used_font_path = "default_exception"
        
        # Log the final font configuration for debugging
        print(f"Final font configuration: path={used_font_path}, size={font_size}")
        
        # Wrap text to fit width - use more robust calculation
        try:
            # Get actual font metrics for better text wrapping
            test_bbox = draw.textbbox((0, 0), "W", font=font)  # Use 'W' as it's typically the widest character
            avg_char_width = test_bbox[2] - test_bbox[0]
            chars_per_line = max(20, int(text_width / avg_char_width))
            wrapped_lines = textwrap.wrap(text, width=chars_per_line)
            print(f"Text wrapping: {len(wrapped_lines)} lines, {chars_per_line} chars per line")
            
            # Ensure we have at least some line breaks for readability
            if len(wrapped_lines) == 1 and len(text) > 50:
                # Force line breaks for long text
                mid_point = len(text) // 2
                # Find a good break point (space near middle)
                for i in range(mid_point - 10, mid_point + 10):
                    if i < len(text) and text[i] == ' ':
                        mid_point = i
                        break
                wrapped_lines = [text[:mid_point].strip(), text[mid_point:].strip()]
                print(f"Forced line break: {wrapped_lines}")
                
        except Exception as wrap_error:
            print(f"Error in text wrapping calculation: {wrap_error}")
            # Fallback to simple wrapping
            avg_char_width = font_size * 0.6
            chars_per_line = max(20, int(text_width / avg_char_width))
            wrapped_lines = textwrap.wrap(text, width=chars_per_line)
        
        # Calculate total text height with better line spacing
        try:
            # Get actual line height from font metrics
            test_bbox = draw.textbbox((0, 0), "Ay", font=font)  # Use 'Ay' to get proper line height
            line_height = (test_bbox[3] - test_bbox[1]) + 10  # Add 10px spacing
        except Exception as height_error:
            print(f"Error calculating line height: {height_error}")
            line_height = font_size + 10  # Fallback
        
        total_text_height = len(wrapped_lines) * line_height
        
        # Center the text vertically
        start_y = max(0, (text_height - total_text_height) // 2)
        
        print(f"Text layout: {len(wrapped_lines)} lines, line_height={line_height}, total_height={total_text_height}")
        
        # Draw each line
        for i, line in enumerate(wrapped_lines):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Get text bbox to center horizontally
            bbox = draw.textbbox((0, 0), line, font=font)
            text_line_width = bbox[2] - bbox[0]
            x = max(0, (text_width - text_line_width) // 2)
            y = start_y + (i * line_height)
            
            # Draw text with outline for better visibility
            outline_width = 2
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 128))
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=(*color_rgb, 255))
            print(f"Drew line {i+1}: '{line}' at position ({x}, {y})")
        
        # Convert PIL image to numpy array for MoviePy
        img_array = np.array(img)
        
        # Create ImageClip
        text_clip = ImageClip(img_array, transparent=True, duration=duration)
        text_clip = text_clip.set_position('center')
        
        print(f"Created text clip with PIL: {text_width}x{text_height}, {len(wrapped_lines)} lines")
        print(f"Text content: {wrapped_lines}")
        print(f"Text clip final dimensions: {text_clip.w}x{text_clip.h}, duration: {text_clip.duration}s")
        return text_clip
        
    except Exception as e:
        print(f"Error creating text with PIL: {e}")
        import traceback
        traceback.print_exc()
        
        # Ultimate fallback: create a simple colored rectangle
        from moviepy.video.VideoClip import ColorClip
        fallback_clip = ColorClip(
            size=(int(video_width * 0.8), 100), 
            color=(255, 255, 255), 
            duration=duration
        ).set_position('center')
        print("Created fallback colored rectangle")
        return fallback_clip

def create_text_clip_with_moviepy(text, video_width, video_height, font_size, text_color, duration):
    """Create a high-quality text clip using MoviePy's TextClip with ImageMagick"""
    try:
        import textwrap
        print(f"Attempting MoviePy TextClip: text='{text[:50]}...', size={video_width}x{video_height}, font_size={font_size}, color={text_color}")
        
        # Ensure text is properly formatted
        if not text or not text.strip():
            print("Warning: Empty or whitespace-only text provided")
            text = "No text provided"
        
        # Normalize text
        text = text.strip()
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Calculate optimal text width for wrapping
        text_width_chars = int((video_width * 0.8) / (font_size * 0.6))
        wrapped_lines = textwrap.wrap(text, width=max(20, text_width_chars))
        formatted_text = '\n'.join(wrapped_lines)
        
        # Get actually available fonts
        available_font_files = get_available_fonts()
        
        # Railway-compatible font options - start with detected fonts
        font_options = available_font_files[:5]  # Try first 5 detected fonts
        
        # Add generic font names as fallback
        font_options.extend([
            'DejaVu-Sans',
            'Liberation-Sans', 
            'Ubuntu',
            'Arial',
            'Helvetica',
            'sans-serif'  # Generic fallback
        ])
        
        # Try each font option
        text_clip = None
        for font_option in font_options:
            try:
                print(f"🔤 Trying font: {font_option}")
                
                # Simpler TextClip parameters for better compatibility
                text_clip = TextClip(
                    formatted_text,
                    fontsize=font_size,
                    color=text_color,
                    font=font_option
                ).set_duration(duration).set_position('center')
                
                print(f"✅ Successfully created TextClip with: {font_option}")
                return text_clip
                
            except Exception as e:
                print(f"❌ Failed with {font_option}: {str(e)[:100]}...")
                continue
        
        # If all MoviePy options failed, fallback to enhanced PIL
        print("⚠️ All MoviePy font options failed, using enhanced PIL rendering")
        return create_enhanced_pil_text_clip(text, video_width, video_height, font_size, text_color, duration)
        
    except Exception as e:
        print(f"❌ Error in MoviePy text creation: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to enhanced PIL
        return create_enhanced_pil_text_clip(text, video_width, video_height, font_size, text_color, duration)

def create_enhanced_pil_text_clip(text, video_width, video_height, font_size, text_color, duration):
    """Enhanced PIL text rendering with better quality settings and extensive debugging"""
    try:
        from moviepy.video.VideoClip import ImageClip
        import textwrap
        
        print(f"🔍 DEBUG: Creating enhanced PIL text clip")
        print(f"🔍 DEBUG: Input - text='{text[:50]}...', size={video_width}x{video_height}, font_size={font_size}, color={text_color}")
        
        # Ensure text is properly formatted
        if not text or not text.strip():
            print("⚠️ Warning: Empty or whitespace-only text provided")
            text = "No text provided"
        
        # Normalize text
        text = text.strip()
        import re
        text = re.sub(r'\s+', ' ', text)
        print(f"🔍 DEBUG: Normalized text: '{text}'")
        
        # Render at 4x resolution for much better quality
        scale_factor = 4
        text_width = int(video_width * 0.9 * scale_factor)
        text_height = int(video_height * 0.8 * scale_factor)
        scaled_font_size = font_size * scale_factor
        
        print(f"🔍 DEBUG: Scaled dimensions: {text_width}x{text_height}, font_size={scaled_font_size}")
        
        # Create high-resolution image with WHITE background for debugging
        img = Image.new('RGBA', (text_width, text_height), (255, 255, 255, 255))  # White background
        draw = ImageDraw.Draw(img)
        
        # Parse color - handle hex colors like '#ffffff' or named colors like 'white'
        if text_color.startswith('#'):
            text_color = text_color.lstrip('#')
            color_rgb = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            color_map = {
                'white': (255, 255, 255), 'black': (0, 0, 0), 'red': (255, 0, 0),
                'green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0),
                'cyan': (0, 255, 255), 'magenta': (255, 0, 255)
            }
            color_rgb = color_map.get(text_color.lower(), (255, 255, 255))
        
        print(f"🔍 DEBUG: Color RGB: {color_rgb}")
        
        # Use our bundled high-quality fonts first
        available_fonts = get_available_fonts()
        font = None
        
        if available_fonts:
            for font_path in available_fonts[:3]:  # Try first 3 fonts
                try:
                    font = ImageFont.truetype(font_path, scaled_font_size)
                    print(f"✅ Using high-quality font: {os.path.basename(font_path)} at size {scaled_font_size}")
                    break
                except Exception as e:
                    print(f"❌ Failed to load {font_path}: {e}")
                    continue
        
        if font is None:
            print("⚠️ No TrueType fonts available, using default font")
            font = ImageFont.load_default()
            scaled_font_size = max(scaled_font_size * 2, 100)
        
        # Text wrapping with better calculations
        avg_char_width = scaled_font_size * 0.6
        chars_per_line = max(20, int(text_width / avg_char_width))
        wrapped_lines = textwrap.wrap(text, width=chars_per_line)
        
        print(f"🔍 DEBUG: Wrapped into {len(wrapped_lines)} lines: {wrapped_lines}")
        
        # Calculate layout
        line_height = int(scaled_font_size * 1.2)
        total_text_height = len(wrapped_lines) * line_height
        start_y = max(0, (text_height - total_text_height) // 2)
        
        print(f"🔍 DEBUG: Layout - line_height={line_height}, total_height={total_text_height}, start_y={start_y}")
        
        # Draw each line with debugging
        for i, line in enumerate(wrapped_lines):
            if not line.strip():
                continue
            
            bbox = draw.textbbox((0, 0), line, font=font)
            text_line_width = bbox[2] - bbox[0]
            x = max(0, (text_width - text_line_width) // 2)
            y = start_y + (i * line_height)
            
            print(f"🔍 DEBUG: Drawing line {i+1}: '{line}' at ({x}, {y})")
            
            # Draw text with BLACK outline for maximum visibility
            outline_width = 4 * scale_factor
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))  # Black outline
            
            # Draw main text in the specified color
            draw.text((x, y), line, font=font, fill=(*color_rgb, 255))
            print(f"✅ Drew line {i+1} with color {color_rgb}")
        
        # Save debug image to see what we're creating
        debug_path = os.path.join('temp', f'debug_text_{uuid.uuid4().hex[:8]}.png')
        os.makedirs('temp', exist_ok=True)
        img.save(debug_path)
        print(f"🔍 DEBUG: Saved text image to {debug_path}")
        
        # Resize back to original resolution with high-quality resampling
        final_width = int(video_width * 0.9)
        final_height = int(video_height * 0.8)
        img = img.resize((final_width, final_height), Image.LANCZOS)
        
        print(f"🔍 DEBUG: Final image size: {img.size}")
        
        # Convert to numpy array
        img_array = np.array(img)
        print(f"🔍 DEBUG: Image array shape: {img_array.shape}")
        print(f"🔍 DEBUG: Image array min/max values: {img_array.min()}/{img_array.max()}")
        
        # Create ImageClip
        text_clip = ImageClip(img_array, transparent=True, duration=duration)
        text_clip = text_clip.set_position('center')
        
        print(f"✅ Created enhanced PIL text clip: {final_width}x{final_height}")
        return text_clip
        
    except Exception as e:
        print(f"❌ Error creating enhanced PIL text: {e}")
        import traceback
        traceback.print_exc()
        # Ultimate fallback
        return create_text_clip_with_pil(text, video_width, video_height, font_size, text_color, duration)

def create_simple_visible_text_clip(text, video_width, video_height, font_size, text_color, duration):
    """Create a simple, guaranteed-visible text clip using PIL with default font"""
    try:
        from moviepy.video.VideoClip import ImageClip
        import textwrap
        
        print(f"🎯 Creating SIMPLE visible text: '{text[:50]}...'")
        
        # Ensure text is properly formatted
        if not text or not text.strip():
            text = "No text provided"
        
        text = text.strip()
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Use a reasonable text area
        text_width = int(video_width * 0.8)
        text_height = int(video_height * 0.6)
        
        # Create image with transparent background
        img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Parse color
        if text_color.startswith('#'):
            text_color = text_color.lstrip('#')
            color_rgb = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            color_rgb = (255, 255, 255)  # Default to white
        
        # Use default font but make it larger for visibility
        font = ImageFont.load_default()
        effective_font_size = max(font_size * 3, 80)  # Make it much larger
        
        # Simple text wrapping
        avg_char_width = effective_font_size * 0.6
        chars_per_line = max(15, int(text_width / avg_char_width))
        wrapped_lines = textwrap.wrap(text, width=chars_per_line)
        
        print(f"📝 Wrapped into {len(wrapped_lines)} lines")
        
        # Calculate layout
        line_height = effective_font_size + 20
        total_text_height = len(wrapped_lines) * line_height
        start_y = max(0, (text_height - total_text_height) // 2)
        
        # Draw each line with maximum visibility
        for i, line in enumerate(wrapped_lines):
            if not line.strip():
                continue
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), line, font=font)
            text_line_width = bbox[2] - bbox[0]
            x = max(0, (text_width - text_line_width) // 2)
            y = start_y + (i * line_height)
            
            print(f"✍️ Drawing line {i+1}: '{line}' at ({x}, {y})")
            
            # Draw THICK black outline for maximum visibility
            outline_width = 6
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=(*color_rgb, 255))
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Create ImageClip
        text_clip = ImageClip(img_array, transparent=True, duration=duration)
        text_clip = text_clip.set_position('center')
        
        print(f"✅ Created simple visible text clip: {text_width}x{text_height}")
        return text_clip
        
    except Exception as e:
        print(f"❌ Error in simple text creation: {e}")
        import traceback
        traceback.print_exc()
        
        # Ultimate fallback - just a colored rectangle with text
        from moviepy.video.VideoClip import ColorClip
        fallback_clip = ColorClip(
            size=(int(video_width * 0.8), 200), 
            color=(255, 255, 255), 
            duration=duration
        ).set_position('center')
        print("⚠️ Created fallback colored rectangle")
        return fallback_clip

def create_story_video(poem_text, video_url, audio_url, font_size, text_color, duration, output_path):
    """Create Instagram story video with poem overlay"""
    temp_video_path = None  # Track temporary video file for cleanup
    try:
        print(f"Creating video with: poem='{poem_text[:50]}...', video_url='{video_url}', duration={duration}")
        
        # Download video if URL provided, otherwise use default
        if video_url and video_url.strip():
            try:
                # For remote URLs, download to temp file first
                if video_url.startswith('http'):
                    print(f"Downloading remote video: {video_url}")
                    
                    # Download video to temporary file
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    # Add specific headers for different sources
                    if 'pexels.com' in video_url:
                        headers['Authorization'] = Config.PEXELS_API_KEY
                    
                    response = requests.get(video_url, headers=headers, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Create temporary file for video
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                        for chunk in response.iter_content(chunk_size=8192):
                            temp_video.write(chunk)
                        temp_video_path = temp_video.name
                    
                    # Load video from temporary file
                    video_clip = VideoFileClip(temp_video_path)
                    print(f"Downloaded and loaded remote video: {video_clip.w}x{video_clip.h}, duration: {video_clip.duration}s")
                    print(f"Video file size: {os.path.getsize(temp_video_path)} bytes")
                    
                    # Clean up temp file after loading (VideoFileClip keeps file handle)
                    # We'll clean it up after video processing is done
                    
                else:
                    video_clip = VideoFileClip(video_url)
                    print(f"Loaded local video: {video_clip.w}x{video_clip.h}, duration: {video_clip.duration}s")
            except Exception as e:
                print(f"Error loading video from {video_url}: {e}")
                import traceback
                traceback.print_exc()
                # Create a simple colored background as fallback
                from moviepy.video.VideoClip import ColorClip
                video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
                print("Using fallback background due to video loading error")
        else:
            # Create a simple colored background - Instagram story format
            from moviepy.video.VideoClip import ColorClip
            video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
            print(f"Created fallback video: {video_clip.w}x{video_clip.h}, duration: {video_clip.duration}s")
        
        # Trim video to desired duration
        if video_clip.duration > duration:
            video_clip = video_clip.subclip(0, duration)
        
        # Ensure video has valid dimensions
        print(f"Video dimensions check: {video_clip.w}x{video_clip.h}")
        if not (hasattr(video_clip, 'w') and hasattr(video_clip, 'h') and video_clip.w > 0 and video_clip.h > 0):
            print(f"Invalid video dimensions detected: w={getattr(video_clip, 'w', 'N/A')}, h={getattr(video_clip, 'h', 'N/A')}, creating fallback")
            from moviepy.video.VideoClip import ColorClip
            video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
        else:
            print("Video dimensions are valid, proceeding with actual video")
        
        # Ensure minimum font size for readability
        min_font_size = 40
        effective_font_size = max(font_size, min_font_size)
        print(f"Font size: requested={font_size}, effective={effective_font_size}")
        
        # Create text using simple, guaranteed-visible rendering
        text_clip = create_simple_visible_text_clip(
            poem_text, 
            video_clip.w, 
            video_clip.h, 
            effective_font_size, 
            text_color, 
            duration
        )
        
        # Add audio if provided
        if audio_url and audio_url.strip():
            try:
                # For remote URLs, download audio first to avoid streaming issues
                if audio_url.startswith('http'):
                    print(f"Downloading remote audio: {audio_url}")
                    
                    # Download audio to temporary file
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'audio/*,*/*;q=0.9'
                    }
                    
                    response = requests.get(audio_url, headers=headers, stream=True, timeout=15)
                    response.raise_for_status()
                    
                    # Create temporary file for audio
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                        for chunk in response.iter_content(chunk_size=8192):
                            temp_audio.write(chunk)
                        temp_audio_path = temp_audio.name
                    
                    # Load audio from temporary file
                    audio_clip = AudioFileClip(temp_audio_path)
                    print(f"Downloaded and loaded remote audio: {audio_clip.duration}s")
                    
                    # Clean up temp file after loading
                    try:
                        os.unlink(temp_audio_path)
                    except:
                        pass
                else:
                    audio_clip = AudioFileClip(audio_url)
                    print(f"Loaded local audio: {audio_clip.duration}s")
                
                # Validate audio duration
                if audio_clip.duration <= 0:
                    print("Invalid audio duration, skipping audio")
                    audio_clip.close()
                elif audio_clip.duration > duration:
                    audio_clip = audio_clip.subclip(0, duration)
                    print(f"Trimmed audio to: {audio_clip.duration}s")
                
                # Only add audio if it's valid
                if audio_clip.duration > 0:
                    video_clip = video_clip.set_audio(audio_clip)
                    print(f"Added audio: {audio_clip.duration}s")
                else:
                    audio_clip.close()
                    
            except Exception as e:
                print(f"Error adding audio from {audio_url}: {e}")
                import traceback
                traceback.print_exc()
                print("Continuing without audio...")
                pass  # Continue without audio if there's an error
        
        # Composite video and text
        final_clip = CompositeVideoClip([video_clip, text_clip])
        
        # Write output file with improved error handling
        try:
            print(f"📹 Writing video: {output_path}")
            print(f"📊 Video info: {video_clip.w}x{video_clip.h}, duration: {final_clip.duration}s")
            
            # First attempt: full quality with audio
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None,
                temp_audiofile='temp_audio.m4a',
                remove_temp=True
            )
            print("✅ Video created successfully with audio")
            
        except Exception as e:
            print(f"❌ Error writing video with audio: {e}")
            
            # Second attempt: lower quality settings
            try:
                print("🔄 Trying with lower quality settings...")
                final_clip = final_clip.without_audio()
                
                # Use more conservative settings for Railway
                final_clip.write_videofile(
                    output_path,
                    fps=24,
                    codec='libx264',
                    bitrate='2000k',  # Lower bitrate
                    verbose=False,
                    logger=None,
                    temp_audiofile=None,
                    remove_temp=True
                )
                print("✅ Video created successfully without audio (lower quality)")
                
            except Exception as e2:
                print(f"❌ Error with lower quality: {e2}")
                
                # Third attempt: even more conservative
                try:
                    print("🔄 Trying with very conservative settings...")
                    
                    # Resize if video is too large (4K might be too much for Railway)
                    if video_clip.w > 1920 or video_clip.h > 1920:
                        print(f"📏 Resizing from {video_clip.w}x{video_clip.h} to 1080x1920")
                        video_clip_resized = video_clip.resize(height=1920)
                        text_clip_resized = text_clip.resize(height=1920)
                        final_clip = CompositeVideoClip([video_clip_resized, text_clip_resized])
                    
                    final_clip.write_videofile(
                        output_path,
                        fps=15,  # Lower FPS
                        codec='libx264',
                        preset='ultrafast',  # Fastest encoding
                        bitrate='1000k',     # Even lower bitrate
                        verbose=False,
                        logger=None
                    )
                    print("✅ Video created successfully with conservative settings")
                    
                except Exception as e3:
                    print(f"❌ All video writing attempts failed: {e3}")
                    raise e3
        
        # Clean up
        video_clip.close()
        text_clip.close()
        final_clip.close()
        
        # Clean up temporary video file if it exists
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.unlink(temp_video_path)
                print(f"Cleaned up temporary video file: {temp_video_path}")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up temporary file {temp_video_path}: {cleanup_error}")
        
        print(f"Video created successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating video: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up temporary video file if it exists (even on error)
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.unlink(temp_video_path)
                print(f"Cleaned up temporary video file after error: {temp_video_path}")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up temporary file after error {temp_video_path}: {cleanup_error}")
        
        return False

if __name__ == '__main__':
    # Use environment variable for port, default to 5001 for local development
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) # Cache bust: Sun Jul 20 01:34:12 PDT 2025
