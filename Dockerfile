FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for Chromium
RUN apt-get update && apt-get install -y \
    wget curl unzip fonts-liberation libnss3 libxss1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libgbm-dev \
    libgtk-4-1 libgraphene-1.0-0 libgstgl-1.0-0 \
    libgstcodecparsers-1.0-0 libavif15 libenchant-2-2 \
    libsecret-1-0 libmanette-0.2-0 libgles2-mesa \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && playwright install

# Copy the app code
COPY scraper.py .

CMD ["python", "scraper.py"]