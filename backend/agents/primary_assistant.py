from typing import Dict, Any
from .base_agent import BaseAgent
from .dietary_assessment_agent import DietaryAssessmentAgent
from .user_agent import UserAgent

class PrimaryAssistant(BaseAgent):
    """Primary AI assistant that routes requests to specialized agents as needed."""

    def __init__(self):
        super().__init__()
        self.system_message = """You are the primary AI assistant for Wellchemy, a health and wellness platform.
Your job is to help users and delegate specific tasks to other expert agents when needed.
Be friendly, helpful, and efficient."""
        self.diet_agent = DietaryAssessmentAgent()
        self.user_agent = UserAgent()

    def _is_diet_question(self, message: str) -> bool:
        keywords = ['diet', 'nutrition', 'food', 'fruit', 'vegetables', 'grains', 'screener']
        return any(word in message.lower() for word in keywords)

    def _is_diet_assessment_request(self, message: str) -> bool:
        keywords = ['take the diet assessment', 'start diet assessment', 'diet survey', 'diet screener', 'do the diet quiz']
        return any(phrase in message.lower() for phrase in keywords)

    def _is_user_question(self, message: str) -> bool:
        keywords = ['login', 'log in', 'sign up', 'register', 'onboard', 'create account', 'account']
        return any(word in message.lower() for word in keywords)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default')

        if self._is_diet_assessment_request(user_message):
            return self.diet_agent.process({"message": "", "user_id": user_id})

        if self._is_diet_question(user_message):
            return self.diet_agent.process({"message": user_message, "user_id": user_id})

        if self._is_user_question(user_message):
            return self.user_agent.process({"message": user_message, "username": user_id})

        # Default general handling
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message}
        ]
        response = self.get_completion(messages)
        return self._format_response(True, "Response generated successfully", data={"response": response})
