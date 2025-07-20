"""
Utility functions for text2story-generator
Contains text processing, font handling, and image generation utilities
"""

import os
import time
import glob
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def cleanup_old_temp_files(temp_folder):
    """Clean up temporary files older than 1 hour"""
    try:
        current_time = time.time()
        
        # Track cleanup statistics
        cleaned_files = 0
        
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                
                # Clean up files older than 1 hour
                if file_age > 3600:
                    try:
                        os.unlink(file_path)
                        cleaned_files += 1
                        print(f"Cleaned up old temp file: {filename}")
                    except Exception as e:
                        print(f"Could not clean up {filename}: {e}")
        
        if cleaned_files > 0:
            print(f"🧹 Cleanup complete: {cleaned_files} files removed")
            
    except Exception as e:
        print(f"Error during temp file cleanup: {e}")

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

def clean_text_preserving_line_breaks(text):
    """Clean up text while preserving intentional line breaks and spacing"""
    if not text or not text.strip():
        return "No text provided"
    
    # Clean up text but preserve intentional line breaks
    text = text.strip()
    # Remove excessive whitespace but keep line breaks
    import re
    # Replace multiple spaces with single space, but preserve line breaks
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove empty lines but keep intentional spacing
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Keep non-empty lines
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1] != '':  # Add single empty line for spacing
            cleaned_lines.append('')
    
    # Join back with proper line breaks
    return '\n'.join(cleaned_lines)

def parse_color(text_color):
    """Parse color string to RGB tuple"""
    if text_color.startswith('#'):
        # Convert hex to RGB
        text_color = text_color.lstrip('#')
        return tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))
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
        return color_map.get(text_color.lower(), (255, 255, 255))

def load_font_with_fallback(font_size, font_paths=None):
    """Load font with comprehensive fallback options"""
    if font_paths is None:
        font_paths = [
            # Bundled font (highest priority)
            os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'Roboto-Bold.woff2'),
            # System fonts that are commonly available
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf',
            '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',
            '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/TTF/LiberationSans-Bold.ttf',
            # Additional common paths
            '/System/Library/Fonts/Helvetica.ttc',  # macOS
            '/System/Library/Fonts/Arial.ttf',      # macOS
            'C:/Windows/Fonts/arial.ttf',           # Windows
            'C:/Windows/Fonts/calibri.ttf',         # Windows
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
            font = ImageFont.load_default()
            used_font_path = "default"
            print("Using default font - truetype fonts not found")
        except Exception as e:
            print(f"Error loading default font: {e}")
            font = ImageFont.load_default()
            used_font_path = "default_fallback"
    
    return font, used_font_path

def process_text_lines(text, font_size, text_width):
    """Process text lines with intelligent wrapping"""
    processed_lines = []
    for line in text.split('\n'):
        if not line.strip():
            processed_lines.append('')  # Keep empty lines for spacing
            continue
        
        # For lines that are too long, wrap them intelligently
        if len(line) > 40:  # If line is very long, wrap it
            # Calculate optimal wrap width based on font size
            avg_char_width = font_size * 0.6
            chars_per_line = max(25, int((text_width * 0.8) / avg_char_width))
            import textwrap
            wrapped = textwrap.wrap(line, width=chars_per_line)
            processed_lines.extend(wrapped)
        else:
            processed_lines.append(line)
    
    return processed_lines

def calculate_line_height(draw, font, font_size):
    """Calculate optimal line height from font metrics"""
    try:
        # Get actual line height from font metrics
        test_bbox = draw.textbbox((0, 0), "Ay", font=font)  # Use 'Ay' to get proper line height
        return (test_bbox[3] - test_bbox[1]) + int(font_size * 0.3)  # Add 30% spacing
    except Exception as height_error:
        print(f"Error calculating line height: {height_error}")
        return font_size + 10  # Fallback

def create_text_preview_image_in_memory(text, font_size, text_color):
    """Generates a preview image in memory and returns the PIL Image object."""
    try:
        # Clean and process text
        text = clean_text_preserving_line_breaks(text)
        
        # Use Instagram story dimensions (9:16 aspect ratio)
        text_width = 1080
        text_height = 1920
        
        # Create image with black background
        img = Image.new('RGB', (text_width, text_height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Parse color
        color_rgb = parse_color(text_color)
        
        # Calculate effective font size (scale up for better quality)
        effective_font_size = max(font_size * 2, 80)
        
        # Load font
        font, used_font_path = load_font_with_fallback(effective_font_size)
        
        if font is None:
            print("⚠️ No system fonts found, using default font")
            font = ImageFont.load_default()
            effective_font_size = max(font_size * 3, 100)  # Make default font larger
        
        # Process text lines with intelligent wrapping
        processed_lines = process_text_lines(text, effective_font_size, text_width)
        
        print(f"📝 Processed into {len(processed_lines)} lines for preview")
        
        # Calculate optimal line height and spacing
        line_height = calculate_line_height(draw, font, effective_font_size)
        
        # Calculate total text height
        total_text_height = len(processed_lines) * line_height
        
        # Center the text vertically
        start_y = max(0, (text_height - total_text_height) // 2)
        
        print(f"📏 Line height: {line_height}, Total height: {total_text_height}")
        
        # Draw each line with enhanced visibility
        for i, line in enumerate(processed_lines):
            if not line.strip():
                continue  # Skip empty lines in drawing
            
            # Get text dimensions for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_line_width = bbox[2] - bbox[0]
            text_line_height = bbox[3] - bbox[1]
            
            # Center horizontally
            x = max(0, (text_width - text_line_width) // 2)
            y = start_y + (i * line_height)
            
            print(f"✍️ Drawing line {i+1}: '{line}' at ({x}, {y})")
            
            # Draw text with enhanced outline for maximum visibility
            outline_width = max(3, effective_font_size // 20)  # Proportional outline
            
            # Draw black outline for contrast
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=color_rgb)
        
        print(f"✅ Created high-quality text preview image in memory")
        return img
        
    except Exception as e:
        print(f"❌ Error creating text preview image in memory: {e}")
        import traceback
        traceback.print_exc()
        return None

def image_to_base64_data_url(img):
    """Convert PIL Image to base64 data URL"""
    try:
        # Convert to base64 data URL
        buffer = BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        # Encode as base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None 