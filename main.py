#!/usr/bin/env python
"""
Simple Telegram bot that integrates with Voiceflow.
Press Ctrl-C on the command line to stop the bot.
"""

import os
import logging
from threading import Thread, Event
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from flask import Flask, jsonify

from telegram_handler import TelegramHandler
from config import TELEGRAM_BOT_TOKEN
from logger import logger

# Create Flask app
app = Flask(__name__)

# Create Telegram application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
telegram_handler = TelegramHandler()

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

# Function to run the bot with proper async handling
def run_bot():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())
    loop.run_forever()

# Bot status tracking
bot_started = Event()

# Start bot thread
bot_thread = Thread(target=run_bot)
bot_thread.daemon = True  # Thread will exit when main thread exits
bot_thread.start()
logger.info("Bot thread started")

@app.route('/health')
def health_check():
    try:
        if bot_thread.is_alive() and application.bot.bot.get_me():
            return jsonify({
                "status": "healthy",
                "bot": "running",
                "timestamp": datetime.now().isoformat()
            }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
    return jsonify({
        "status": "unhealthy",
        "bot": "stopped",
        "timestamp": datetime.now().isoformat()
    }), 500

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "version": "1.0",
        "description": "Voiceflow Telegram Bot",
        "endpoints": {
            "health": "/health",
            "root": "/"
        }
    }), 200

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
