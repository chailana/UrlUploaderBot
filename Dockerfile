# Use an official lightweight Python image.
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install necessary system packages and dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for the application
WORKDIR /app

# Copy the requirements file into the image
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy all the application files into the image
COPY . .

# Expose the port your app runs on, if needed
# EXPOSE 8080 (only if your bot runs on a web server)

# Run the bot (change bot.py to your main file if needed)
CMD gunicorn app:app & python3 InfinityBots.py
