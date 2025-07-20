# Deploying Text2Story Generator to Railway

## 🚀 Quick Deploy to Railway

### Option 1: Deploy via Railway CLI (Recommended)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize and Deploy**
   ```bash
   # Navigate to your project directory
   cd text2story-generator
   
   # Initialize Railway project
   railway init
   
   # Deploy to Railway
   railway up
   ```

### Option 2: Deploy via GitHub Integration

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Connect to Railway**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect the Flask app and deploy

## 🔧 Environment Variables Setup

After deployment, set up your environment variables in Railway:

1. Go to your project in Railway Dashboard
2. Click on "Variables" tab
3. Add the following environment variables:

```
OPENAI_API_KEY=your_openai_api_key
PEXELS_API_KEY=your_pexels_api_key
JAMENDO_API_KEY=your_jamendo_api_key
GOOGLE_SHEETS_CREDENTIALS=your_google_sheets_credentials_json
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
```

## 📋 Required API Keys

### OpenAI API Key
- Go to [OpenAI Platform](https://platform.openai.com/)
- Create account and get API key
- Add to Railway variables

### Pexels API Key
- Go to [Pexels API](https://www.pexels.com/api/)
- Sign up and get API key
- Add to Railway variables

### Jamendo API Key (Optional)
- Go to [Jamendo Developer Portal](https://developer.jamendo.com/)
- Sign up for free account
- Create application and get API key
- Add to Railway variables

### Google Sheets Credentials (Optional)
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create project and enable Google Sheets API
- Create service account and download JSON credentials
- Add entire JSON as Railway variable

## 🌐 Access Your Live App

After successful deployment:
- Railway will provide a URL like: `https://your-app-name.railway.app`
- Your app will be live and accessible worldwide!

## 🔍 Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check Railway logs for error messages
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version in `runtime.txt`

2. **Environment Variables**
   - Make sure all required API keys are set
   - Check variable names match exactly

3. **Video Processing Issues**
   - Railway includes FFmpeg via `imageio-ffmpeg`
   - If issues persist, check MoviePy configuration

4. **Port Issues**
   - Railway automatically sets `PORT` environment variable
   - App is configured to use this automatically

### Checking Logs:
```bash
railway logs
```

### Redeploying:
```bash
railway up
```

## 🎯 Next Steps

1. **Custom Domain** (Optional)
   - Add custom domain in Railway dashboard
   - Configure DNS settings

2. **Monitoring**
   - Set up Railway monitoring
   - Configure alerts for downtime

3. **Scaling**
   - Railway auto-scales based on traffic
   - Monitor usage in dashboard

## 📞 Support

If you encounter issues:
1. Check Railway logs
2. Verify environment variables
3. Test locally first
4. Contact Railway support if needed

Your Text2Story Generator will be live and ready to create beautiful Instagram stories! 🎉 