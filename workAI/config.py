"""
Agent Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "claude-opus-4-6")

# Memory Configuration
MEMORY_MAX_LENGTH = int(os.getenv("MEMORY_MAX_LENGTH", "100"))
SESSION_ID = os.getenv("SESSION_ID", "default")

# Tool Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_API_URL = "https://api.weather.com/v1/current"
