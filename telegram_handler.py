from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from voiceflow_client import VoiceflowClient
from session_manager import SessionManager
from analytics import Analytics
from logger import logger
import time
import json
from datetime import datetime

class TelegramHandler:
    def __init__(self):
        self.voiceflow_client = VoiceflowClient()
        self.session_manager = SessionManager()
        self.analytics = Analytics()

    def create_inline_keyboard(self, buttons):
        """Create Telegram inline keyboard from buttons"""
        keyboard = []
        row = []
        for button in buttons:
            callback_data = json.dumps({
                "text": button,
                "type": "button"
            })
            row.append(InlineKeyboardButton(button, callback_data=callback_data))
            if len(row) == 2:  # Create rows of 2 buttons
                keyboard.append(row)
                row = []
        if row:  # Add any remaining buttons
            keyboard.append(row)
        return InlineKeyboardMarkup(keyboard)

    async def send_carousel(self, context, chat_id, carousel_data):
        """Send a carousel as multiple cards with inline buttons"""
        try:
            for item in carousel_data:
                caption = f"*{item.get('title', '')}*\n{item.get('description', '')}"
                buttons = item.get('buttons', [])
                keyboard = self.create_inline_keyboard(buttons) if buttons else None

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
        except Exception as e:
            logger.error(f"Error sending carousel: {str(e)}", exc_info=True)
            raise

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callback queries"""
        query = update.callback_query
        await query.answer()  # Acknowledge the button click

        try:
            data = json.loads(query.data)
            # Send the button's text as a message
            request = {
                "request": {
                    "type": "text",
                    "payload": data["text"]
                }
            }

            # Get response from Voiceflow
            response = self.voiceflow_client.interact(
                str(query.from_user.id),
                request,
                self.session_manager.get_context(str(query.from_user.id))
            )
            await self.process_voiceflow_response(update, context, response, query.message.chat_id)

        except Exception as e:
            logger.error(f"Error handling callback query: {str(e)}", exc_info=True)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Sorry, there was an error processing your selection. Please try again."
            )

    async def process_voiceflow_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response, chat_id):
        """Process different types of Voiceflow responses"""
        try:
            processed_response = self.voiceflow_client.process_response(response)

            # Update session context
            if processed_response.get('context'):
                self.session_manager.set_context(str(update.effective_user.id), processed_response['context'])

            # Handle carousel type
            if processed_response.get('carousel'):
                await self.send_carousel(context, chat_id, processed_response['carousel'])
                return

            # Handle card type
            if processed_response.get('card'):
                card = processed_response['card']
                caption = f"*{card.get('title', '')}*\n{card.get('description', '')}"
                keyboard = self.create_inline_keyboard(card.get('buttons', [])) if card.get('buttons') else None

                if card.get('image'):
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=card['image'],
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
                return

            # Send image if present
            if processed_response['image_url']:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=processed_response['image_url']
                )

            # Send text with buttons if present
            if processed_response['text']:
                keyboard = self.create_inline_keyboard(processed_response['buttons']) if processed_response['buttons'] else None
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=processed_response['text'],
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error processing Voiceflow response: {str(e)}", exc_info=True)
            await context.bot.send_message(
                chat_id=chat_id,
                text="I encountered an error processing the response. Please try again."
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages from Telegram"""
        try:
            start_time = time.time()
            user_id = str(update.effective_user.id)
            message_text = update.message.text

            logger.info(f"Received message from user {user_id}: {message_text[:50]}...")

            # Add user message to history
            self.session_manager.add_to_history(user_id, message_text)

            # Get current session context
            session_context = self.session_manager.get_context(user_id)

            # Prepare request for Voiceflow
            request = {
                "request": {
                    "type": "text",
                    "payload": message_text
                }
            }

            # Get response from Voiceflow with context
            response = self.voiceflow_client.interact(user_id, request, session_context)
            
            # Process and send response
            await self.process_voiceflow_response(update, context, response, update.effective_chat.id)

            # Calculate and log analytics
            latency = time.time() - start_time
            self.analytics.log_interaction(
                user_id=user_id,
                user_message=message_text,
                bot_response=self.voiceflow_client.process_response(response),
                latency=latency
            )

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="I'm sorry, but I encountered an error. Please try again later."
            )

    async def clear_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear user session data"""
        user_id = str(update.effective_user.id)
        self.session_manager.clear_session(user_id)
        logger.info(f"Cleared session for user {user_id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Your session has been reset."
        )

    async def get_analytics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get analytics for the requesting user"""
        user_id = str(update.effective_user.id)
        metrics = self.analytics.get_user_metrics(user_id)
        
        if metrics:
            message = (
                f"Your Chat Statistics:\n"
                f"Total messages: {metrics['total_messages']}\n"
                f"Button clicks: {metrics['button_clicks']}\n"
                f"Images received: {metrics['images_received']}\n"
                f"First interaction: {metrics['first_interaction']}\n"
                f"Last interaction: {metrics['last_interaction']}"
            )
        else:
            message = "No analytics data available for your account yet."
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
