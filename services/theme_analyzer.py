import openai
from config import Config
import json

class ThemeAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def analyze_poem_theme(self, poem_text):
        """
        Analyze a poem to extract themes, mood, and suggest appropriate visual/audio elements
        """
        try:
            prompt = f"""
            Analyze the following poem and provide:
            1. Main themes (e.g., love, nature, sadness, joy, etc.)
            2. Mood/tone (e.g., melancholic, uplifting, peaceful, dramatic, etc.)
            3. Visual keywords for stock video search (e.g., "ocean waves", "sunset", "rain", "forest")
            4. Audio mood suggestions (e.g., "calm ambient", "upbeat", "melancholic piano", "nature sounds")
            5. Color palette suggestions (e.g., "warm oranges and reds", "cool blues and greens")
            
            Poem: {poem_text}
            
            Return the analysis as a JSON object with these keys:
            - themes: list of main themes
            - mood: string describing the overall mood
            - visual_keywords: list of keywords for video search
            - audio_suggestions: list of audio mood suggestions
            - color_palette: string describing suggested colors
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative assistant that analyzes poetry and suggests visual and audio elements for video content creation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            analysis_text = response.choices[0].message.content
            # Try to parse as JSON, fallback to structured text if needed
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                analysis = self._parse_text_analysis(analysis_text)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing poem theme: {e}")
            return self._get_default_analysis()
    
    def _parse_text_analysis(self, text):
        """Fallback parser for when JSON parsing fails"""
        analysis = {
            "themes": ["poetry", "reflection"],
            "mood": "contemplative",
            "visual_keywords": ["abstract", "nature"],
            "audio_suggestions": ["ambient", "piano"],
            "color_palette": "neutral tones"
        }
        
        # Simple keyword extraction
        text_lower = text.lower()
        
        # Extract themes
        theme_keywords = ["love", "nature", "sadness", "joy", "hope", "despair", "peace", "war", "time", "memory"]
        found_themes = [theme for theme in theme_keywords if theme in text_lower]
        if found_themes:
            analysis["themes"] = found_themes
        
        # Extract mood
        mood_keywords = {
            "melancholic": ["sad", "melancholy", "sorrow", "grief"],
            "uplifting": ["joy", "happy", "bright", "hope"],
            "peaceful": ["calm", "peace", "tranquil", "serene"],
            "dramatic": ["intense", "dramatic", "passionate", "fierce"]
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                analysis["mood"] = mood
                break
        
        return analysis
    
    def _get_default_analysis(self):
        """Return default analysis when API fails"""
        return {
            "themes": ["poetry", "reflection"],
            "mood": "contemplative",
            "visual_keywords": ["abstract", "nature", "light"],
            "audio_suggestions": ["ambient", "piano", "soft"],
            "color_palette": "neutral tones"
        }
    
    def suggest_video_keywords(self, themes, mood):
        """Generate specific video search keywords based on themes and mood"""
        keyword_mappings = {
            "love": ["romantic sunset", "couple walking", "heart shapes", "rose petals"],
            "nature": ["forest", "ocean waves", "mountains", "flowers blooming"],
            "sadness": ["rain", "gray sky", "lonely road", "falling leaves"],
            "joy": ["sunshine", "laughing people", "bright colors", "celebration"],
            "peace": ["calm water", "gentle breeze", "soft clouds", "meditation"],
            "melancholic": ["dramatic clouds", "moody lighting", "solitude", "reflection"],
            "uplifting": ["sunrise", "bright colors", "movement", "energy"],
            "peaceful": ["gentle nature", "soft lighting", "tranquil scenes", "serenity"]
        }
        
        keywords = []
        for theme in themes:
            if theme in keyword_mappings:
                keywords.extend(keyword_mappings[theme])
        
        if mood in keyword_mappings:
            keywords.extend(keyword_mappings[mood])
        
        # Remove duplicates and return
        return list(set(keywords))[:5]  # Limit to 5 keywords 