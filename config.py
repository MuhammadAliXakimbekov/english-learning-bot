import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Gemini API Configuration  
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

# Bot Configuration
MAX_MESSAGE_LENGTH = 4096
RATE_LIMIT_PER_USER = 10
RATE_LIMIT_WINDOW_MS = 60000  # 1 minute

# Voice processing configuration
VOICE_DOWNLOAD_PATH = './temp/'
VOICE_FORMAT = 'ogg' 