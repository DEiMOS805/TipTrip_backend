# syntax=docker/dockerfile:1
FROM python:3.11.5-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container to /app.
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    libasound-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    python3-dev \
    build-essential \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Set librosa permissions
RUN chmod -R 777 /usr/local/lib/python3.11/site-packages/librosa/

# Copy the source code into the container and set the correct ownership
COPY . .

# Grant permissions to the entrypoint script
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application using a entrypoint script
ENTRYPOINT [ "./entrypoint.sh" ]
