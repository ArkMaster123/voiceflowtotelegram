import os
import logging
import json
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import TelegramError, BadRequest, TimedOut, NetworkError
from dotenv import load_dotenv
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
VOICEFLOW_API_KEY = os.getenv('VOICEFLOW_API_KEY')
VOICEFLOW_PROJECT_ID = os.getenv('VOICEFLOW_PROJECT_ID')

class VoiceflowError(Exception):
    """Custom exception for Voiceflow API errors"""
    pass

async def talk_to_voiceflow(user_id: int, request: Dict[str, Any]) -> Dict[str, Any]:
    """Interact with Voiceflow API with enhanced error handling"""
    url = f'https://general-runtime.voiceflow.com/state/user/{user_id}/interact'
    headers = {
        'Authorization': VOICEFLOW_API_KEY,
        'versionID': 'production',
        'Content-Type': 'application/json'
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json={'request': request}, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to Voiceflow for user {user_id}")
        raise VoiceflowError("Connection to Voiceflow timed out")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} from Voiceflow: {e.response.text}")
        raise VoiceflowError(f"Voiceflow API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Unexpected error talking to Voiceflow: {str(e)}")
        raise VoiceflowError("Unexpected error communicating with Voiceflow")

async def save_chat(user_id: int) -> None:
    """Save conversation transcript with error handling"""
    url = "https://api.voiceflow.com/v2/transcripts"
    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "projectID": VOICEFLOW_PROJECT_ID,
        "versionID": "production",
        "sessionID": str(user_id)
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Successfully saved transcript for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save transcript for user {user_id}: {str(e)}")
        # Don't raise exception as this is non-critical

def create_inline_keyboard(buttons: list) -> Optional[InlineKeyboardMarkup]:
    """Create Telegram inline keyboard with error handling"""
    try:
        keyboard = []
        row = []
        for button in buttons:
            if not isinstance(button, dict) or "name" not in button or "request" not in button:
                logger.warning("Invalid button format")
                continue

            callback_data = json.dumps({
                "request": button["request"],
                "name": button["name"]
            })

            # Telegram has a 64-byte limit for callback_data
            if len(callback_data.encode('utf-8')) > 64:
                logger.warning(f"Callback data too long for button: {button['name']}")
                continue

            row.append(InlineKeyboardButton(button["name"], callback_data=callback_data))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        return InlineKeyboardMarkup(keyboard) if keyboard else None
    except Exception as e:
        logger.error(f"Error creating keyboard: {str(e)}")
        return None

async def send_carousel(context: ContextTypes.DEFAULT_TYPE, chat_id: int, carousel_data: list) -> None:
    """Send carousel with error handling"""
    for item in carousel_data:
        try:
            caption = f"*{item.get('title', '')}*\n{item.get('description', '')}"
            buttons = item.get('buttons', [])
            keyboard = create_inline_keyboard(buttons) if buttons else None

            if item.get('image'):
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=item['image'],
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
        except BadRequest as e:
            logger.error(f"Telegram API error sending carousel item: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending carousel item: {str(e)}")

async def handle_trace(update: Update, context: ContextTypes.DEFAULT_TYPE, trace: Dict[str, Any]) -> None:
    """Handle different types of Voiceflow traces with error handling"""
    chat_id = update.effective_chat.id

    try:
        if not isinstance(trace, dict) or 'type' not in trace or 'payload' not in trace:
            logger.warning(f"Invalid trace format: {trace}")
            return

        if trace['type'] == 'text':
            await context.bot.send_message(
                chat_id=chat_id,
                text=trace['payload'].get('message', 'No message content'),
                parse_mode='Markdown'
            )

        elif trace['type'] == 'choice':
            keyboard = create_inline_keyboard(trace['payload'].get('buttons', []))
            if keyboard:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Please choose an option:",
                    reply_markup=keyboard
                )

        elif trace['type'] == 'visual':
            image_url = trace['payload'].get('image', {}).get('url')
            if image_url:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=image_url
                )

        elif trace['type'] == 'carousel':
            await send_carousel(context, chat_id, trace['payload'].get('items', []))

        elif trace['type'] == 'card':
            caption = f"*{trace['payload'].get('title', '')}*\n{trace['payload'].get('description', '')}"
            buttons = trace['payload'].get('buttons', [])
            keyboard = create_inline_keyboard(buttons) if buttons else None

            if trace['payload'].get('image'):
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=trace['payload']['image'],
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )

    except BadRequest as e:
        logger.error(f"Telegram API error handling trace: {str(e)}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, I couldn't display that content properly."
        )
    except Exception as e:
        logger.error(f"Error handling trace: {str(e)}")

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks with error handling"""
    query = update.callback_query
    await query.answer()

    try:
        data = json.loads(query.data)
        response = await talk_to_voiceflow(query.message.chat_id, data['request'])

        for trace in response:
            await handle_trace(update, context, trace)

        await save_chat(query.message.chat_id)

    except json.JSONDecodeError:
        logger.error("Invalid button callback data")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Sorry, there was an error with that button."
        )
    except VoiceflowError as e:
        logger.error(f"Voiceflow error handling button: {str(e)}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Sorry, I'm having trouble processing your selection right now."
        )
    except Exception as e:
        logger.error(f"Unexpected error handling button: {str(e)}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Sorry, something went wrong. Please try again."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages with error handling"""
    try:
        response = await talk_to_voiceflow(update.message.chat_id, {
            'type': 'text',
            'payload': update.message.text
        })

        for trace in response:
            await handle_trace(update, context, trace)

        await save_chat(update.message.chat_id)

    except VoiceflowError as e:
        logger.error(f"Voiceflow error: {str(e)}")
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm having trouble understanding right now. Please try again in a moment."
        )
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Sorry, something went wrong. Please try again."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with error handling"""
    try:
        response = await talk_to_voiceflow(update.message.chat_id, {'type': 'launch'})

        for trace in response:
            await handle_trace(update, context, trace)

        await save_chat(update.message.chat_id)

    except VoiceflowError as e:
        logger.error(f"Voiceflow error in start command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm having trouble starting up. Please try again in a moment."
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Hello! I'm having some technical difficulties. Please try again shortly."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot"""
    logger.error(f"Update {update} caused error {context.error}")

    try:
        if isinstance(context.error, NetworkError):
            message = "Sorry, I'm having network issues. Please try again in a moment."
        elif isinstance(context.error, TimedOut):
            message = "The request timed out. Please try again."
        elif isinstance(context.error, BadRequest):
            message = "Sorry, I couldn't process that request."
        else:
            message = "An unexpected error occurred. Please try again."

        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")

def run_bot() -> None:
    """Run the bot with error handling"""
    try:
        # Create application
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(CallbackQueryHandler(handle_button_click))

        # Add error handler
        app.add_error_handler(error_handler)

        # Run bot
        logger.info("Bot is starting...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Fatal error starting bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Validate environment variables
    if not all([TELEGRAM_BOT_TOKEN, VOICEFLOW_API_KEY, VOICEFLOW_PROJECT_ID]):
        logger.critical("Missing required environment variables!")
        sys.exit(1)

    run_bot()