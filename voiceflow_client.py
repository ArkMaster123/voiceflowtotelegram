import requests
from typing import Dict, List, Optional
from config import VOICEFLOW_API_KEY, VOICEFLOW_API_BASE_URL
from logger import logger

class VoiceflowClient:
    def __init__(self):
        self.api_key = VOICEFLOW_API_KEY
        self.base_url = VOICEFLOW_API_BASE_URL
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json',
            'versionID': 'production'  # Always use production version
        }

    def interact(self, user_id: str, request: Dict, context: Dict = None) -> List[Dict]:
        """
        Interact with the Voiceflow dialog manager
        """
        try:
            endpoint = f"{self.base_url}/state/user/{user_id}/interact"
            
            # Include context in the request if provided
            if context:
                request['context'] = context

            response = requests.post(
                endpoint,
                headers=self.headers,
                json=request,
                timeout=10  # Add timeout for better error handling
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while connecting to Voiceflow API for user {user_id}")
            raise Exception("Connection timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Voiceflow API error: {str(e)}")
            raise Exception("Failed to communicate with Voiceflow. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected error in Voiceflow interaction: {str(e)}")
            raise

    def process_response(self, response: List[Dict]) -> Dict:
        """
        Process Voiceflow response and extract relevant information
        """
        try:
            result = {
                'text': None,
                'buttons': [],
                'image_url': None,
                'context': {},
                'carousel': None,
                'card': None
            }

            for trace in response:
                trace_type = trace.get('type')
                payload = trace.get('payload', {})
                
                if trace_type == 'speak' or trace_type == 'text':
                    if result['text'] is None:
                        result['text'] = payload.get('message', '')
                    else:
                        result['text'] += f"\n{payload.get('message', '')}"
                
                elif trace_type == 'choice':
                    result['buttons'].extend([
                        button.get('name')
                        for button in payload.get('buttons', [])
                    ])
                
                elif trace_type == 'visual':
                    if 'image' in payload:
                        result['image_url'] = payload['image']
                
                elif trace_type == 'carousel':
                    result['carousel'] = payload.get('items', [])
                
                elif trace_type == 'card':
                    result['card'] = {
                        'title': payload.get('title'),
                        'description': payload.get('description'),
                        'image': payload.get('image'),
                        'buttons': [btn.get('name') for btn in payload.get('buttons', [])]
                    }
                
                elif trace_type == 'context':
                    result['context'].update(payload)

            return result

        except Exception as e:
            logger.error(f"Error processing Voiceflow response: {str(e)}")
            raise Exception("Error processing bot response. Please try again.")
