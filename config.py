import os
from pathlib import Path
from dotenv import load_dotenv

# Load the right env file based on APP_ENV (default: local)
APP_ENV = os.getenv("APP_ENV", "local")
env_file = Path(f".env.{APP_ENV}")
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # fallback to plain .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ZAI_API_KEY = os.getenv("ZAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANCEDB_PATH = os.getenv("LANCEDB_PATH", ".lancedb_local")

# Model routing — fast/cheap for intake, powerful for analysis
INTAKE_MODEL = "gpt-4o-mini"
ANALYSIS_MODEL = "claude-sonnet-4-6"
OUTPUT_MODEL = "claude-sonnet-4-6"

AVAILABLE_MODELS = {
    "Fast (GPT-4o mini)": "gpt-4o-mini",
    "Balanced (GPT-4o)": "gpt-4o",
    "Thorough (Claude Sonnet)": "claude-sonnet-4-6",
}
