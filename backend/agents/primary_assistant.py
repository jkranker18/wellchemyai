from typing import Dict, Any
from openai import OpenAI
import os
from .base_agent import BaseAgent

class PrimaryAssistant(BaseAgent):
    """Primary AI assistant that handles general queries and coordinates with other agents."""
    
    def __init__(self):
        """Initialize the Primary Assistant with GPT-3.5-turbo."""
        super().__init__()
        self.system_message = """You are the primary AI assistant for Wellchemy, a wellness and health platform. 
        Your role is to provide helpful, accurate, and supportive responses to general queries about health, wellness, 
        and the platform's features. Always maintain a professional yet friendly tone."""
    
    def process(self, data):
        """Process user messages and provide appropriate responses."""
        user_message = data['message']
        
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message}
        ]
        
        response = self.get_completion(messages)
        return self._format_response(
            success=True,
            message="Response generated successfully",
            data={"response": response}
        ) 