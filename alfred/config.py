"""Configuration for Alfred Gemini"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Alias

# Use whichever is set
API_KEY = GOOGLE_API_KEY or GEMINI_API_KEY

if not API_KEY:
    print("Warning: No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in .env")

# Model Configuration
GEMINI_PRO_MODEL = "gemini-1.5-pro"
GEMINI_FLASH_MODEL = "gemini-1.5-flash"
DEFAULT_MODEL = GEMINI_FLASH_MODEL  # Use Flash for speed

# Audio Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5  # Seconds of silence before processing

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
AUDIO_CACHE = PROJECT_ROOT / ".cache" / "audio"
AUDIO_CACHE.mkdir(parents=True, exist_ok=True)

# Conversation
MAX_HISTORY_LENGTH = 20  # Keep last N messages
CONVERSATION_TIMEOUT = 300  # 5 minutes

# Voice
VOICE_NAME = "en-US-Neural2-D"  # Google Cloud TTS voice
SPEAKING_RATE = 1.0
PITCH = 0.0
