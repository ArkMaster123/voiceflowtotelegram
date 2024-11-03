# voiceflowtotelegram
# Telegram Voiceflow Bot

A Telegram bot that integrates with Voiceflow to provide interactive conversations with support for cards, carousels, and inline buttons.

## Features
- Text messages handling
- Interactive buttons
- Image cards
- Carousels
- Error handling
- Conversation transcript saving

## Prerequisites
- Python 3.11+
- Telegram Bot Token
- Voiceflow API Key
- Voiceflow Project ID

## Installation

### Using Docker
1. Clone the repository
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. Create .env file from example
```bash
cp .env.example .env
```

3. Edit .env with your credentials
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
VOICEFLOW_API_KEY=your_voiceflow_api_key
VOICEFLOW_PROJECT_ID=your_project_id
```

4. Build and run with Docker
```bash
docker build -t telegram-voiceflow-bot .
docker run -d --env-file .env telegram-voiceflow-bot
```

### Manual Installation
1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Set up environment variables as above

3. Run the bot
```bash
python main.py
```

## Development
- The bot uses python-telegram-bot for Telegram integration
- Voiceflow API is used for conversation management
- Logging is configured to both file and console

## License
