import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Voiceflow configuration
VOICEFLOW_API_KEY = os.getenv('VOICEFLOW_API_KEY')
VOICEFLOW_PROJECT_ID = os.getenv('VOICEFLOW_PROJECT_ID')
VOICEFLOW_API_BASE_URL = 'https://general-runtime.voiceflow.com'

# Application configuration
LOG_LEVEL = 'INFO'
