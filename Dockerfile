# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    # --home "/nonexistent" \
    --shell "/sbin/nologin" \
    # --no-create-home \
    --uid "${UID}" \
    appuser

RUN mkdir -p /home/appuser && chown appuser:appuser /home/appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
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

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Set librosa permissions
RUN chmod -R 777 /usr/local/lib/python3.11/site-packages/librosa/

# Set correct permissions for /app and change ownership to the non-privileged user
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user to run the application.
USER appuser
COPY --chown=appuser:appuser . .

# Copy the source code into the container.
# COPY . .

# Set permissions for /app after copying the files
RUN chmod -R 775 /app

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application.
CMD ["python3", "main.py"]
