import google.generativeai as genai
from config import GEMINI_API_KEY, MAX_MESSAGE_LENGTH

class GeminiService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_text(self, prompt, context='', mode='general'):
        """Generate text response using Gemini with mode-specific context"""
        try:
            # Add mode-specific context
            mode_contexts = {
                'writing': "You are an expert writing tutor. Help with grammar, style, structure, and creative writing. Be encouraging and provide specific suggestions.",
                'speaking': "You are a speaking coach and pronunciation expert. Help with speaking skills, pronunciation, conversation, and public speaking. Be supportive and practical.",
                'reading': "You are a reading comprehension expert and literature tutor. Help with text analysis, vocabulary, reading strategies, and understanding complex texts.",
                'listening': "You are an audio analysis and listening comprehension expert. Help with understanding audio content, note-taking, and listening skills.",
                'general': "You are a helpful educational AI assistant. Provide clear, informative, and encouraging responses to learning questions."
            }
            
            mode_context = mode_contexts.get(mode, mode_contexts['general'])
            full_prompt = f"{mode_context}\n\nContext: {context}\n\nUser: {prompt}" if context else f"{mode_context}\n\nUser: {prompt}"
            
            response = self.model.generate_content(full_prompt)
            text = response.text
            
            # Truncate if response is too long for Telegram
            if len(text) > MAX_MESSAGE_LENGTH:
                text = text[:MAX_MESSAGE_LENGTH - 3] + '...'
            
            return text
        except Exception as error:
            print(f'Error generating text with Gemini: {error}')
            raise Exception('Failed to generate response. Please try again later.')
    
    async def transcribe_voice(self, audio_buffer):
        """Transcribe voice message (placeholder)"""
        try:
            # For voice transcription, we'll use a simple approach
            # In a real implementation, you might want to use a dedicated speech-to-text service
            # For now, we'll return a placeholder message
            return "Voice message received. I'm currently processing your voice input."
        except Exception as error:
            print(f'Error transcribing voice: {error}')
            raise Exception('Failed to transcribe voice message. Please try again.')
    
    async def process_message(self, message, is_voice=False, mode='general'):
        """Process message with Gemini"""
        try:
            if is_voice:
                # For voice messages, we'll return a placeholder for now
                # In a real implementation, you would process the audio file
                return "I received your voice message. Voice processing is currently being implemented. Please send a text message for now."
            
            return await self.generate_text(message, mode=mode)
        except Exception as error:
            print(f'Error processing message: {error}')
            raise error

# Create a global instance
gemini_service = GeminiService() 