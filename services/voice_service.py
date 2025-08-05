import os
import requests
from config import TELEGRAM_BOT_TOKEN, VOICE_DOWNLOAD_PATH, VOICE_FORMAT
import time

class VoiceService:
    def __init__(self):
        # Ensure temp directory exists
        if not os.path.exists(VOICE_DOWNLOAD_PATH):
            os.makedirs(VOICE_DOWNLOAD_PATH, exist_ok=True)
    
    async def download_voice_file(self, file_id, bot):
        """Download voice file from Telegram"""
        try:
            file = await bot.get_file(file_id)
            file_path = file.file_path
            
            if not file_path:
                raise Exception('Could not get file path')
            
            file_name = f"{int(time.time())}_{file_id}.{VOICE_FORMAT}"
            local_path = os.path.join(VOICE_DOWNLOAD_PATH, file_name)
            
            # Download the file
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return local_path
        except Exception as error:
            print(f'Error downloading voice file: {error}')
            raise Exception('Failed to download voice file')
    
    async def transcribe_voice(self, audio_path):
        """Transcribe voice message (placeholder)"""
        try:
            # For now, we'll return a placeholder message
            # In a real implementation, you would:
            # 1. Convert the audio to the right format
            # 2. Send it to a speech-to-text service (like Google Speech-to-Text)
            # 3. Return the transcribed text
            
            return "Voice message transcribed: [This is a placeholder. In a real implementation, this would contain the actual transcribed text from your voice message.]"
        except Exception as error:
            print(f'Error transcribing voice: {error}')
            raise Exception('Failed to transcribe voice message')
        finally:
            # Clean up the downloaded file
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as cleanup_error:
                print(f'Error cleaning up audio file: {cleanup_error}')
    
    async def process_voice_message(self, voice, bot):
        """Process voice message"""
        try:
            # Download the voice file
            audio_path = await self.download_voice_file(voice.file_id, bot)
            
            # Transcribe the voice
            transcription = await self.transcribe_voice(audio_path)
            
            return transcription
        except Exception as error:
            print(f'Error processing voice message: {error}')
            raise error

# Create a global instance
voice_service = VoiceService() 