# Use a stable Debian-based Python image (works well with audio libs & torch CPU)
ARG PYTHON_BASE=python:3.11-bullseye
FROM ${PYTHON_BASE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps required for audio processing and building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc ffmpeg libsndfile1 libsndfile1-dev curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
# (Your requirements file lives at newBackend/requirements.txt)
COPY newBackend/requirements.txt /app/requirements.txt

# Upgrade pip and install Python deps
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install -r /app/requirements.txt
    
# Install PyTorch separately to optimize layer caching
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0+cpu torchvision==0.16.0+cpu --extra-index-url https://pypi.org/simple \
 && pip install -r /app/requirements.txt    

# Copy backend code into the image
COPY newBackend /app

# Ensure dataset and models dirs exist (may be overridden by docker-compose mounts)
RUN mkdir -p /app/dataset/enrolment /app/models && chown -R root:root /app

# Add non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy entrypoint and make it executable
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the app port
EXPOSE 5000

# Entrypoint will prepare folders/permissions (see script)
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command: adjust "run:app" if your Flask app module or variable differs
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
