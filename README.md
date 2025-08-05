# Education Bot 🤖 (Python Version)

A Telegram bot powered by Google's Gemini AI that provides educational assistance through text and voice interactions, built with Python.

## Features

- **Text Conversations**: Chat with the bot using text messages
- **Voice Message Support**: Send voice messages (transcription coming soon)
- **Rate Limiting**: Per-user rate limiting to prevent abuse
- **Error Handling**: Comprehensive error handling and user feedback
- **Educational Focus**: Optimized for educational content and explanations

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Telegram Bot Token (already configured)
- Gemini API Key (already configured)

## Installation

1. Clone or download this project
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. The bot is already configured with the provided API keys in `config.py`

## Usage

### Starting the Bot

```bash
# Start the bot
python main.py
```

### Bot Commands

- `/start` - Welcome message and bot information
- `/help` - Detailed help and usage instructions
- `/status` - Check your current rate limit status

### Message Types

#### Text Messages
Send any text message to the bot and receive an AI-generated response using Gemini.

#### Voice Messages
Send voice messages to the bot. Currently returns a placeholder message while voice transcription is being implemented.

#### Audio Files
Send audio files and the bot will attempt to process them (same as voice messages).

## Configuration

The bot configuration is stored in `config.py`:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `GEMINI_API_KEY`: Your Gemini API key
- `MAX_MESSAGE_LENGTH`: Maximum length for bot responses (4096 characters)
- `RATE_LIMIT_PER_USER`: Number of messages allowed per user per minute (10)
- `RATE_LIMIT_WINDOW_MS`: Time window for rate limiting (60000ms = 1 minute)

## Project Structure

```
education-bot/
├── main.py                 # Main bot file
├── config.py              # Configuration and API keys
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── utils/
│   └── rate_limiter.py   # Rate limiting functionality
└── services/
    ├── gemini_service.py  # Gemini AI integration
    └── voice_service.py   # Voice message processing
```

## Rate Limiting

The bot implements per-user rate limiting to prevent abuse:

- **Limit**: 10 messages per minute per user
- **Window**: 1 minute sliding window
- **Commands**: Use `/status` to check your current limit

## Error Handling

The bot includes comprehensive error handling:

- API errors are caught and user-friendly messages are sent
- Rate limit exceeded messages with countdown
- Network and file processing errors
- Graceful shutdown on keyboard interrupt

## Voice Processing

Voice message processing is currently implemented with placeholder functionality:

1. **Download**: Voice files are downloaded to a temporary directory
2. **Transcription**: Placeholder for speech-to-text conversion
3. **Cleanup**: Temporary files are automatically deleted
4. **Response**: Currently returns a placeholder message

To implement full voice transcription, you would need to:
- Integrate with a speech-to-text service (Google Speech-to-Text, Whisper, etc.)
- Convert audio formats as needed
- Process the transcribed text through Gemini

## Development

### Adding New Features

1. Create new service files in the `services/` directory
2. Add new command handlers in `main.py`
3. Update rate limiting if needed
4. Test thoroughly before deployment

### Logging

The bot includes comprehensive logging for monitoring performance and debugging.

## Security

- API keys are stored in configuration files (consider using environment variables in production)
- Rate limiting prevents abuse
- Error messages don't expose sensitive information
- Temporary files are automatically cleaned up

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if the bot token is valid
2. **API errors**: Verify your Gemini API key is correct
3. **Rate limiting**: Wait for the rate limit window to reset
4. **Voice not working**: Voice processing is currently a placeholder
5. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Logs

Check the console output for detailed error messages and response times.

## Dependencies

- `python-telegram-bot`: Telegram Bot API wrapper
- `google-generativeai`: Google's Gemini AI API
- `requests`: HTTP library for file downloads
- `python-dotenv`: Environment variable management

## License

MIT License - feel free to modify and distribute as needed.

## Support

For issues or questions, check the error logs and ensure all dependencies are properly installed. 