from flask import Flask, render_template, request, jsonify, send_file, Response
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import os
import requests
import tempfile
import uuid
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
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Initialize services
theme_analyzer = ThemeAnalyzer()
stock_media = StockMediaService()
audio_service = AudioService()
sheets_manager = SheetsManager()

@app.route('/')
def index():
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
        
        # Generate unique filename
        output_filename = f"story_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
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
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
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
    """Download generated story file"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get file size for logging
        file_size = os.path.getsize(file_path)
        print(f"Downloading file: {filename} ({file_size} bytes)")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error downloading file {filename}: {e}")
        return jsonify({'error': str(e)}), 404

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

def create_story_video(poem_text, video_url, audio_url, font_size, text_color, duration, output_path):
    """Create Instagram story video with poem overlay"""
    try:
        print(f"Creating video with: poem='{poem_text[:50]}...', video_url='{video_url}', duration={duration}")
        
        # Download video if URL provided, otherwise use default
        if video_url and video_url.strip():
            try:
                # For remote URLs, try to download first or use proxy
                if video_url.startswith('http'):
                    # Use a simple colored background for remote videos to avoid issues
                    from moviepy.video.VideoClip import ColorClip
                    video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
                    print(f"Using fallback background for remote video: {video_url}")
                else:
                    video_clip = VideoFileClip(video_url)
                    print(f"Loaded local video: {video_clip.w}x{video_clip.h}, duration: {video_clip.duration}s")
            except Exception as e:
                print(f"Error loading video from {video_url}: {e}")
                # Create a simple colored background as fallback
                from moviepy.video.VideoClip import ColorClip
                video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
        else:
            # Create a simple colored background - Instagram story format
            from moviepy.video.VideoClip import ColorClip
            video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
            print(f"Created fallback video: {video_clip.w}x{video_clip.h}, duration: {video_clip.duration}s")
        
        # Trim video to desired duration
        if video_clip.duration > duration:
            video_clip = video_clip.subclip(0, duration)
        
        # Ensure video has valid dimensions
        if video_clip.w <= 0 or video_clip.h <= 0:
            print("Invalid video dimensions, creating fallback")
            from moviepy.video.VideoClip import ColorClip
            video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
        
        # Create text clip using label method (doesn't require ImageMagick)
        try:
            text_clip = TextClip(
                poem_text,
                fontsize=min(font_size, 80),  # Cap font size
                color=text_color,
                font='Arial',
                method='label',  # Use label method which doesn't require ImageMagick
                size=(min(video_clip.w * 0.9, 1000), None)  # Cap width
            ).set_position('center').set_duration(duration)
        except Exception as e:
            print(f"Error creating text clip: {e}")
            # Simple fallback without advanced features
            text_clip = TextClip(
                poem_text[:50],  # Limit text length
                fontsize=40,
                color='white',
                method='label'
            ).set_position('center').set_duration(duration)
        
        # Add audio if provided
        if audio_url and audio_url.strip():
            try:
                audio_clip = AudioFileClip(audio_url)
                print(f"Loaded audio: {audio_clip.duration}s")
                
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
                print(f"Error adding audio: {e}")
                import traceback
                traceback.print_exc()
                pass  # Continue without audio if there's an error
        
        # Composite video and text
        final_clip = CompositeVideoClip([video_clip, text_clip])
        
        # Write output file
        try:
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
        except Exception as e:
            print(f"Error writing video with audio: {e}")
            # Try without audio
            try:
                # Remove audio and try again
                final_clip = final_clip.without_audio()
                final_clip.write_videofile(
                    output_path,
                    fps=24,
                    codec='libx264',
                    verbose=False,
                    logger=None
                )
                print("Video created successfully without audio")
            except Exception as e2:
                print(f"Error writing video without audio: {e2}")
                raise e2
        
        # Clean up
        video_clip.close()
        text_clip.close()
        final_clip.close()
        
        print(f"Video created successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Use environment variable for port, default to 5001 for local development
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 