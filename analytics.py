import json
from datetime import datetime
from typing import Dict, List, Optional
from logger import logger

class Analytics:
    def __init__(self):
        self.user_metrics: Dict[str, dict] = {}
        self.conversation_logs: List[dict] = []

    def log_interaction(self, user_id: str, user_message: str, bot_response: dict, latency: float):
        """Log a single interaction between user and bot"""
        timestamp = datetime.now().isoformat()
        
        # Update user metrics
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = {
                'total_messages': 0,
                'total_interactions': 0,
                'first_interaction': timestamp,
                'last_interaction': timestamp,
                'button_clicks': 0,
                'images_received': 0
            }
        
        metrics = self.user_metrics[user_id]
        metrics['total_messages'] += 1
        metrics['total_interactions'] += 1
        metrics['last_interaction'] = timestamp
        
        if bot_response.get('image_url'):
            metrics['images_received'] += 1
        if user_message in (bot_response.get('buttons') or []):
            metrics['button_clicks'] += 1

        # Log conversation details
        interaction_log = {
            'timestamp': timestamp,
            'user_id': user_id,
            'user_message': user_message,
            'bot_response': {
                'text': bot_response.get('text'),
                'has_buttons': bool(bot_response.get('buttons')),
                'has_image': bool(bot_response.get('image_url'))
            },
            'latency': latency
        }
        
        self.conversation_logs.append(interaction_log)
        logger.info(f"Interaction logged - User: {user_id}, Message: {user_message[:50]}...")

    def get_user_metrics(self, user_id: str) -> Optional[dict]:
        """Get metrics for a specific user"""
        return self.user_metrics.get(user_id)

    def get_global_metrics(self) -> dict:
        """Get global usage metrics"""
        total_users = len(self.user_metrics)
        total_messages = sum(m['total_messages'] for m in self.user_metrics.values())
        total_button_clicks = sum(m['button_clicks'] for m in self.user_metrics.values())
        total_images = sum(m['images_received'] for m in self.user_metrics.values())

        return {
            'total_users': total_users,
            'total_messages': total_messages,
            'total_button_clicks': total_button_clicks,
            'total_images': total_images,
            'average_messages_per_user': total_messages / total_users if total_users > 0 else 0
        }

    def export_logs(self, file_path: str = 'conversation_logs.json'):
        """Export conversation logs to a JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.conversation_logs, f, indent=2)
            logger.info(f"Conversation logs exported to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting logs: {str(e)}")
