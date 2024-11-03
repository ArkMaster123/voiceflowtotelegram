from typing import Dict, Optional
import json
from datetime import datetime
from logger import logger

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    def get_session(self, user_id: str) -> dict:
        """Get or create a session for a user"""
        if user_id not in self._sessions:
            self._sessions[user_id] = {
                'state': {},
                'context': {},
                'last_response': None,
                'conversation_history': [],
                'session_start': datetime.now().isoformat()
            }
        return self._sessions[user_id]

    def update_session(self, user_id: str, data: dict):
        """Update session data for a user"""
        if user_id in self._sessions:
            self._sessions[user_id].update(data)
        else:
            self._sessions[user_id] = data

    def add_to_history(self, user_id: str, message: str, is_user: bool = True):
        """Add a message to the conversation history"""
        session = self.get_session(user_id)
        session['conversation_history'].append({
            'message': message,
            'is_user': is_user,
            'timestamp': datetime.now().isoformat()
        })
        logger.debug(f"Added message to history for user {user_id}")

    def clear_session(self, user_id: str):
        """Clear a user's session data"""
        if user_id in self._sessions:
            logger.info(f"Clearing session for user {user_id}")
            del self._sessions[user_id]

    def get_context(self, user_id: str) -> dict:
        """Get the conversation context for a user"""
        session = self.get_session(user_id)
        return session.get('context', {})

    def set_context(self, user_id: str, context: dict):
        """Set the conversation context for a user"""
        session = self.get_session(user_id)
        session['context'] = context
        logger.debug(f"Updated context for user {user_id}")
