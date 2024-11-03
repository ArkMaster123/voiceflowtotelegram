import os
import asyncio
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from telegram_handler import TelegramHandler
from config import TELEGRAM_BOT_TOKEN
from logger import logger

app = Flask(__name__)
telegram_handler = TelegramHandler()

# Initialize bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome! I'm your Voiceflow-powered assistant. "
        "You can start chatting with me right away!\n\n"
        "Available commands:\n"
        "/start - Start the conversation\n"
        "/clear - Clear your session\n"
        "/stats - View your chat statistics"
    )
    logger.info(f"New user started the bot: {update.effective_user.id}")
    await update.message.reply_text(welcome_message)

# Add handlers
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("clear", telegram_handler.clear_session))
application.add_handler(CommandHandler("stats", telegram_handler.get_analytics))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler.handle_message))
application.add_handler(CallbackQueryHandler(telegram_handler.handle_callback_query))

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "version": "1.0",
        "description": "Voiceflow Telegram Bot"
    }), 200

def main():
    # Initialize the bot
    asyncio.run(application.initialize())
    asyncio.run(application.start())
    logger.info("Bot initialized and started")
    
    # Start Flask server
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
