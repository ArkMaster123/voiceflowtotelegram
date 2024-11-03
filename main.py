#!/usr/bin/env python
"""
Simple Telegram bot that integrates with Voiceflow.
Press Ctrl-C on the command line to stop the bot.
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from telegram_handler import TelegramHandler
from config import TELEGRAM_BOT_TOKEN
from logger import logger

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

def main() -> None:
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    telegram_handler = TelegramHandler()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("clear", telegram_handler.clear_session))
    application.add_handler(CommandHandler("stats", telegram_handler.get_analytics))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler.handle_message))
    application.add_handler(CallbackQueryHandler(telegram_handler.handle_callback_query))

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
