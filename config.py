"""
Configuration management for HR Climate Insight.
Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Anonymity settings (hardcoded - do not change without authorization)
ANONYMITY_THRESHOLD = 5

# Prompt file
MASTER_PROMPT_FILE = PROMPTS_DIR / "master_prompt.txt"


def get_master_prompt() -> str:
    """Load the master prompt template."""
    if not MASTER_PROMPT_FILE.exists():
        raise FileNotFoundError(f"Master prompt not found: {MASTER_PROMPT_FILE}")
    return MASTER_PROMPT_FILE.read_text(encoding='utf-8')


def validate_config() -> list[str]:
    """
    Validate configuration and return list of errors.

    Returns:
        List of error messages (empty if all valid)
    """
    errors = []

    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY not set. Add it to .env file or environment.")

    if not MASTER_PROMPT_FILE.exists():
        errors.append(f"Master prompt file not found: {MASTER_PROMPT_FILE}")

    return errors
