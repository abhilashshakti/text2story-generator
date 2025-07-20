FROM python:3.11-slim

# Install system dependencies including fonts
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fontconfig \
    fonts-dejavu \
    fonts-liberation \
    fonts-roboto \
    fonts-noto \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp uploads static/fonts

# Expose port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"] 