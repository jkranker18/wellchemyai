from typing import Dict, Any
from .base_agent import BaseAgent

class UserAgent(BaseAgent):
    """Agent responsible for handling new user onboarding and login processes."""
    
    def __init__(self):
        """Initialize the User Agent with GPT-3.5-turbo."""
        super().__init__()
        self.system_message = """You are the user management assistant for Wellchemy. 
        Your role is to handle user-related queries, including account management, 
        login issues, and user preferences. Be helpful and professional while ensuring 
        user privacy and security."""
    
    def process(self, data):
        """Process user-related queries and provide appropriate responses."""
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

    def _format_response(self, success: bool, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format the response from the agent.
        
        Args:
            success: Boolean indicating if the operation was successful
            message: String containing the response message
            data: Dictionary containing additional data to be included in the response
            
        Returns:
            Dictionary containing the formatted response
        """
        return {
            "success": success,
            "message": message,
            "data": data
        } 