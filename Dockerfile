# Use a lightweight Node.js base image
FROM node:18-slim

# Install Python 3, pip, and ffmpeg (required for yt-dlp audio conversion)
RUN apt-get update && \
    apt-get install -y python3 python3-pip python-is-python3 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install yt-dlp using pip
# We use --break-system-packages because we are in a container and it's safe
RUN python3 -m pip install yt-dlp --break-system-packages

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --production

# Copy the rest of the application code
COPY . .

# Set environment variable for Python path if needed, though system python3 should be fine
# ENV PYTHON_PATH=python3

# Expose the port the app runs on
EXPOSE 5000

# Start the server
CMD ["node", "server/index.js"]
