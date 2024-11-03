import os
import asyncio
from datetime import datetime
from threading import Thread
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "👋 Welcome! I'm your Voiceflow-powered assistant.\n/start - Start\n/clear - Reset\n/stats - Statistics"
    await update.message.reply_text(welcome_message)

# Add handlers
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("clear", telegram_handler.clear_session))
application.add_handler(CommandHandler("stats", telegram_handler.get_analytics))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler.handle_message))
application.add_handler(CallbackQueryHandler(telegram_handler.handle_callback_query))

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

def run_bot():
    """Run the bot in the background"""
    asyncio.run(application.run_polling())

if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask server
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
