# syntax=docker/dockerfile:1
FROM python:3.11.5-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container to /app.
WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    # --home "/nonexistent" \
    --shell "/sbin/nologin" \
    # --no-create-home \
    --uid "10001" \
    appuser

RUN mkdir -p /home/appuser && chown appuser:appuser /home/appuser

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

# Set correct permissions for /app and change ownership to the non-privileged user
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container using the non-privileged user.
COPY --chown=appuser:appuser . .

# Set permissions for /app after copying the files
RUN chmod -R 777 /app

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application.
# ENTRYPOINT [ "/app/service_entrypoint.sh" ]
CMD ["python3", "main.py"]
