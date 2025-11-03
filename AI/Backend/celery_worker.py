# ...existing code...
import sys
from pathlib import Path

# Ensure project root is on sys.path so `configs.settings` can be imported when running this file directly.
project_root = Path(__file__).resolve().parents[3]  # adjust if your layout differs
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from configs.settings import settings
except Exception as exc:
    raise RuntimeError(
        "Failed to import `configs.settings.settings`. Ensure your project root is on PYTHONPATH "
        "and `configs/settings.py` defines `settings` with CELERY_BROKER_URL and CELERY_RESULT_BACKEND."
    ) from exc

from celery import Celery

# Validate required settings
if not getattr(settings, "CELERY_BROKER_URL", None):
    raise RuntimeError("settings.CELERY_BROKER_URL is not set")
if not getattr(settings, "CELERY_RESULT_BACKEND", None):
    raise RuntimeError("settings.CELERY_RESULT_BACKEND is not set")

# Optional: allow module list to be provided from settings
default_includes = getattr(settings, "CELERY_INCLUDE", None)
if default_includes is not None and not isinstance(default_includes, (list, tuple)):
    raise RuntimeError("settings.CELERY_INCLUDE must be a list or tuple of module paths")

# --- Celery App Initialization ---
celery_app = Celery(
    "voice_system",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=list(default_includes) if default_includes else None,
)

# --- Celery Config ---
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=getattr(settings, "TIMEZONE", "Asia/Kolkata"),
    enable_utc=getattr(settings, "ENABLE_UTC", True),
    # broker_connection_retry_on_startup may not be available in all kombu/celery versions.
    # Only set it if present in settings to avoid unexpected config keys.
    **({"broker_connection_retry_on_startup": True} if getattr(settings, "CELERY_RETRY_ON_STARTUP", True) else {}),
)

# --- Optional: Auto-discover tasks from specified modules ---
# If you prefer autodiscovery instead of `include`, set CELERY_AUTODISCOVER = True and provide
# CELERY_TASK_MODULES = ["your_app.tasks", ...] in settings.
if getattr(settings, "CELERY_AUTODISCOVER", False):
    task_modules = getattr(settings, "CELERY_TASK_MODULES", [])
    if not isinstance(task_modules, (list, tuple)):
        raise RuntimeError("settings.CELERY_TASK_MODULES must be a list or tuple of module paths")
    if task_modules:
        celery_app.autodiscover_tasks(task_modules, force=True)

# --- Entry Point (for CLI execution) ---
if __name__ == "__main__":
    # Running Celery workers is typically done via the `celery` CLI:
    #   celery -A Kavach.AI.Backend.celery_worker worker --loglevel=info
    # This file can be started as a module, but calling .start() expects sys.argv like the celery CLI.
    celery_app.start()
# ...existing code...