import os
from pathlib import Path
from dotenv import load_dotenv

# Load the right env file based on APP_ENV (default: local)
APP_ENV = os.getenv("APP_ENV", "local")
BASE_DIR = Path(__file__).parent
env_file = BASE_DIR / f".env.{APP_ENV}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # fallback to plain .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # optional, kept for compatibility
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # optional, kept for compatibility
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ZAI_API_KEY = os.getenv("ZAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANCEDB_PATH = os.getenv("LANCEDB_PATH", ".lancedb_local")

# Validate required environment variables
_REQUIRED = ["OPENROUTER_API_KEY", "TAVILY_API_KEY"]
_missing = [k for k in _REQUIRED if not globals()[k]]
if _missing:
    raise EnvironmentError(f"Missing required env vars: {', '.join(_missing)}")

# Model routing — fast/cheap for intake, powerful for analysis
INTAKE_MODEL = os.getenv("INTAKE_MODEL", "openai/gpt-4o-mini")
ANALYSIS_MODEL = os.getenv("ANALYSIS_MODEL", "anthropic/claude-sonnet-4-5")
OUTPUT_MODEL = os.getenv("OUTPUT_MODEL", "anthropic/claude-sonnet-4-5")

AVAILABLE_MODELS = {
    "Fast (GPT-4o mini)": "openai/gpt-4o-mini",
    "Balanced (GPT-4o)": "openai/gpt-4o",
    "Thorough (Claude Sonnet)": "anthropic/claude-sonnet-4-5",
}
