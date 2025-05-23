from typing import Dict, Any
from .base_agent import BaseAgent

class UserAgent(BaseAgent):
    """Agent responsible for handling new user onboarding and login processes."""

    def __init__(self):
        super().__init__()
        self.system_message = """You are the user management assistant for Wellchemy. 
Your job is to assist with:
- user onboarding,
- account setup,
- login help,
- managing preferences.

Be friendly, helpful, and clear."""

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = data.get('message', '').lower()
        username = data.get('username', 'guest')

        if "login" in user_message:
            return self._fo_
