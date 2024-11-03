from typing import Optional
import json

def save_conversation_state(user_id: str, state: dict):
    """
    Save conversation state to memory
    """
    try:
        return json.dumps(state)
    except Exception as e:
        return None

def load_conversation_state(user_id: str) -> Optional[dict]:
    """
    Load conversation state from memory
    """
    try:
        return {}  # Initialize empty state for new conversations
    except Exception as e:
        return None
