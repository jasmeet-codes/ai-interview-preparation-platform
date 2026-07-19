"""
config.py
---------
All configuration for the app lives here. Values are pulled from environment
variables (loaded from a local .env file via python-dotenv) so that secrets
like API keys are never hardcoded into the source code.

HOW TO ADD YOUR AI API KEY:
    1. Copy ".env.example" to a new file named ".env" in the project root.
    2. Open ".env" and paste your key on the line:
           OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
    3. Save the file. Flask will pick it up automatically on the next run.
    4. If you don't have a key yet, leave it blank - the app will use a
       built-in mock AI (services/ai_service.py) so you can still demo
       every feature without spending any money.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load variables from a ".env" file sitting next to this file (if present).
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Base configuration shared by all environments."""

    # --- Security ---------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # --- Database -----------------------------------------------------
    DATABASE_PATH = os.path.join(
        BASE_DIR, os.environ.get("DATABASE_PATH", "instance/interview_prep.db")
    )

    # --- AI provider ----------------------------------------------------
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    # True when no key is configured -> the app transparently uses mock AI.
    AI_MOCK_MODE = OPENAI_API_KEY == ""

    # --- File uploads ----------------------------------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "resumes")
    ALLOWED_RESUME_EXTENSIONS = {"pdf"}
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", 5)) * 1024 * 1024

    # --- Misc ----------------------------------------------------------
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"


# Static reference data used across the app (kept here so it's easy to tweak)
CATEGORIES = ["HR", "Technical", "Aptitude", "Coding"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
QUESTIONS_PER_INTERVIEW = 7  # falls within the requested 5-10 range
