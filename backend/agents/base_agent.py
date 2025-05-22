from abc import ABC, abstractmethod
from typing import Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env file from the backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

class BaseAgent(ABC):
    """Base class for all AI agents in the Wellchemy platform."""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1"
        )
        self.model = "gpt-3.5-turbo"
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return a response.
        
        Args:
            input_data: Dictionary containing the input data for the agent
            
        Returns:
            Dictionary containing the agent's response
        """
        pass
    
    def _format_response(self, success: bool, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format the agent's response in a consistent way.
        
        Args:
            success: Whether the operation was successful
            message: A message describing the result
            data: Additional data to include in the response
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "success": success,
            "message": message
        }
        if data:
            response["data"] = data
        return response

    def get_completion(self, messages):
        """Get a completion from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {str(e)}")
            raise 