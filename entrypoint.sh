#!/usr/bin/env bash
set -euo pipefail

# Allow overrides from environment (docker-compose should set VOSK_MODEL_PATH if needed)
MODEL_DIR="${VOSK_MODEL_PATH:-/app/models/vosk-model-small-en-us-0.15}"
DATASET_ENROL_DIR="${DATASET_DIR:-/app/dataset/enrolment}"

# Create expected directories if missing
mkdir -p "$MODEL_DIR" "$DATASET_ENROL_DIR"

# Fix permissions so the non-root user can access mounted host folders
# (This is harmless if directories are already owned appropriately)
chown -R "$(id -u):$(id -g)" /app || true

# Optional: Print debug info to logs for quick verification
echo "[entrypoint] MODEL_DIR = $MODEL_DIR"
echo "[entrypoint] DATASET_ENROL_DIR = $DATASET_ENROL_DIR"
echo "[entrypoint] Starting command: $@"

# Execute the CMD from Dockerfile (gunicorn by default) / any passed command
exec "$@"
