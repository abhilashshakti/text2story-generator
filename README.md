# Text2Story Generator

A comprehensive Instagram story automation tool that transforms poems into beautiful video stories with AI-powered theme analysis, stock media integration, and Google Sheets management.

## 🚀 Features

### Core Functionality
- **AI Theme Analysis**: Uses OpenAI GPT to analyze poem themes, mood, and suggest appropriate visual/audio elements
- **Stock Media Integration**: Automatically fetches relevant videos from Pexels and audio from multiple sources based on theme analysis
- **Video Generation**: Creates Instagram stories with poem text overlaid on background videos with music
- **Google Sheets Management**: Organize and track all your poems and generated stories

### Advanced Features
- **Custom Media Search**: Search for specific videos and audio files
- **Batch Processing**: Process multiple poems from Google Sheets
- **Customizable Styling**: Adjust font size, color, duration, and text positioning
- **Download Management**: Easy download and organization of generated stories
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Video Processing | MoviePy, FFmpeg |
| AI Analysis | OpenAI GPT-3.5 |
| Stock Media | Pexels API, Jamendo API, Spotify API |
| Data Management | Google Sheets API |
| Deployment | Railway, Replit, or AWS Lambda |

## 📋 Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- API keys for:
  - OpenAI
  - Pexels
  - Jamendo (optional)
  - Spotify (optional)
  - Google Sheets (optional)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd text2story-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu**: `sudo apt install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 🔑 API Setup

### OpenAI API
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add to `.env`: `OPENAI_API_KEY=your-key-here`

### Pexels API
1. Go to [Pexels API](https://www.pexels.com/api/)
2. Sign up and get your API key
3. Add to `.env`: `PEXELS_API_KEY=your-key-here`

### Jamendo API (Optional)
1. Go to [Jamendo Developer Portal](https://developer.jamendo.com/)
2. Sign up for a free account
3. Create a new application
4. Copy your API key
5. Add to `.env`: `JAMENDO_API_KEY=your-key-here`

### Spotify API (Optional)
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in app details (name, description)
5. Accept terms and create
6. Copy Client ID and Client Secret
7. Add to `.env`:
   ```
   SPOTIFY_CLIENT_ID=your-client-id
   SPOTIFY_CLIENT_SECRET=your-client-secret
   ```

### Google Sheets API (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API
4. Create a service account and download credentials
5. Add to `.env`: `GOOGLE_SHEETS_CREDENTIALS=your-credentials-json`

## 📖 Usage

### Basic Workflow

1. **Enter Poem**: Paste your poem text into the input field
2. **Analyze Theme**: Click "Analyze Theme" to get AI-powered suggestions
3. **Select Media**: Choose from suggested videos and audio, or search for custom media
4. **Customize**: Adjust font size, color, and duration
5. **Generate**: Click "Generate Story" to create your Instagram story
6. **Download**: Download the generated MP4 file

### Google Sheets Integration

1. **Create Sheet**: Click "Create New Sheet" to set up poem management
2. **Add Poems**: Poems can be added manually or through the app
3. **Track Progress**: Monitor status of all your poems
4. **Batch Processing**: Process multiple poems at once

### Advanced Features

- **Custom Media Search**: Use the search function to find specific videos/audio
- **Theme Analysis**: Get detailed analysis of poem themes and mood
- **Style Customization**: Fine-tune text appearance and video duration
- **Export Options**: Download individual stories or export data to CSV

## 🏗️ Project Structure

```
text2story-generator/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables template
├── README.md            # This file
├── services/            # Service modules
│   ├── theme_analyzer.py    # OpenAI theme analysis
│   ├── stock_media.py       # Pexels integration
│   ├── audio_service.py     # Audio integration
│   └── sheets_manager.py    # Google Sheets management
├── templates/           # HTML templates
│   └── index.html          # Main interface
├── static/              # Static files (CSS, JS, images)
├── uploads/             # Uploaded files
├── outputs/             # Generated stories
└── temp/                # Temporary files
```

## 🚀 Deployment

### Railway
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Replit
1. Import the repository to Replit
2. Set environment variables in Secrets
3. Run the application

### AWS Lambda
1. Package the application with dependencies
2. Create Lambda function
3. Set environment variables
4. Configure API Gateway

## 🔧 Configuration

### Video Settings
- Default duration: 15 seconds
- Default font size: 60px
- Default text color: White
- Supported formats: MP4, AVI, MOV, MKV

### Audio Settings
- Supported formats: MP3, WAV, M4A, AAC
- Automatic volume normalization
- Background music integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🎯 Roadmap

- [ ] Instagram auto-posting integration
- [ ] Batch processing improvements
- [ ] More video effects and transitions
- [ ] Advanced text animations
- [ ] Mobile app version
- [ ] Social media scheduling
- [ ] Analytics dashboard

## 🙏 Acknowledgments

- OpenAI for GPT-3.5 API
- Pexels for stock video API
- Jamendo for free music API
- MoviePy for video processing
- Tailwind CSS for styling 