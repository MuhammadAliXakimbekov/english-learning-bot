import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8306098940:AAEH0Oe8F-OUR5jJEwSf-pIDdEv_hFij_6c')

# Gemini API Configuration  
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDwT1SbqfsqRJP8UtZIYfNbb7jyr0Vw2Y4')

# Bot Configuration
MAX_MESSAGE_LENGTH = 4096
RATE_LIMIT_PER_USER = 10
RATE_LIMIT_WINDOW_MS = 60000  # 1 minute

# Voice processing configuration
VOICE_DOWNLOAD_PATH = './temp/'
VOICE_FORMAT = 'ogg' 