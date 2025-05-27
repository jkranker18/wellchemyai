from typing import Dict, Any
from .base_agent import BaseAgent
from .dietary_assessment_agent import DietaryAssessmentAgent
from .user_agent import UserAgent
from .eligibility_agent import EligibilityAgent

class PrimaryAssistant(BaseAgent):
    """Primary AI assistant that routes requests to specialized agents as needed."""

    def __init__(self):
        super().__init__()
        self.system_message = """You are the primary AI assistant for Wellchemy, a health and wellness platform.
Your job is to help users and delegate specific tasks to other expert agents when needed.
Be friendly, helpful, and efficient."""
        self.diet_agent = DietaryAssessmentAgent()
        self.user_agent = UserAgent()
        self.eligibility_agent = EligibilityAgent()

        # Track which agent is currently handling each user
        self.user_sessions = {}  # user_id -> 'diet', 'user', 'eligibility', or None

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = data.get('message', '')
        user_id = data.get('user_id', None)

        # 🧠 Always route to active agent first
        current = self.user_sessions.get(user_id)

        if current == 'diet':
            response = self.diet_agent.process({"message": user_message, "user_id": user_id})
            if response.get("message") == "Assessment complete":
                self.user_sessions.pop(user_id, None)  # reset session
            return response

        if current == 'eligibility':
            response = self.eligibility_agent.process({"message": user_message, "user_id": user_id})
            if response.get("message") == "Eligibility assessment complete":
                self.user_sessions.pop(user_id, None)
            return response

        if not user_id:
            return self.user_agent.process({"message": user_message})

        # 🧠 If looks like diet response, keep flow with diet agent
        if self._looks_like_diet_response(user_message):
            self.user_sessions[user_id] = 'diet'
            return self.diet_agent.process({"message": user_message, "user_id": user_id})

        # 🟢 Start diet assessment
        if self._is_diet_assessment_request(user_message):
            self.user_sessions[user_id] = 'diet'
            return self.diet_agent.process({"message": "", "user_id": user_id})

        # 📋 Diet question
        if self._is_diet_question(user_message):
            return self.diet_agent.process({"message": user_message, "user_id": user_id})

        # 👤 User account
        if self._is_user_question(user_message):
            return self.user_agent.process({"message": user_message, "username": user_id})

        # ✅ Eligibility
        if self._is_eligibility_request(user_message):
            self.user_sessions[user_id] = 'eligibility'
            return self.eligibility_agent.process({"message": "", "user_id": user_id})

        # 🤖 Default assistant reply
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message}
        ]
        response_text = self.get_completion(messages)
        return self._format_response(True, "Response generated successfully", data={"response": response_text})

    def _is_diet_assessment_request(self, message: str) -> bool:
        keywords = ['take the diet assessment', 'start diet assessment', 'diet survey', 'diet screener', 'do the diet quiz']
        return any(phrase in message.lower() for phrase in keywords)

    def _is_diet_question(self, message: str) -> bool:
        keywords = ['diet', 'nutrition', 'food', 'fruit', 'vegetables', 'grains', 'screener']
        return any(word in message.lower() for word in keywords)

    def _is_user_question(self, message: str) -> bool:
        keywords = ['login', 'log in', 'sign up', 'register', 'onboard', 'create account', 'account']
        return any(word in message.lower() for word in keywords)

    def _is_eligibility_request(self, message: str) -> bool:
        keywords = ['check eligibility', 'am i eligible', 'program check', 'start eligibility']
        return any(word in message.lower() for word in keywords)

    def _looks_like_diet_response(self, message: str) -> bool:
        msg = message.lower()
        freq_keywords = ['never', 'less than', '1-3', '4-6', '1-2', 'more than', 'times', 'per', 'week', 'day', 'x', 'daily', 'weekly']
        return any(k in msg for k in freq_keywords) or msg.replace(".", "").isdigit()
