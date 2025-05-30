from typing import Dict, Any
from .base_agent import BaseAgent
from .dietary_assessment_agent import DietaryAssessmentAgent
from .user_agent import UserAgent
from .eligibility_agent import EligibilityAgent
import os
import json

class PrimaryAssistant(BaseAgent):
    """Primary AI assistant that routes requests to specialized agents as needed."""

    def __init__(self):
        super().__init__()
        self.system_message = """
You are the primary AI assistant for Wellchemy.
Your job is to help users and choose the right function from our internal toolkit when they need help with diet assessment, eligibility, or account access.
Always prefer structured tools when the request matches.
Examples:
- If the user says 'I want to check eligibility' → call check_eligibility
- If they say 'start the diet screener' → call start_diet_assessment
- If it's a general health question, respond directly with helpful advice.
"""

        self.diet_agent = DietaryAssessmentAgent()
        self.user_agent = UserAgent()
        self.eligibility_agent = EligibilityAgent()

        self.user_sessions = {}  # user_id -> 'diet', 'user', 'eligibility', or None

        self.functions = [
            {
                "name": "start_diet_assessment",
                "description": "Starts the structured diet screener questionnaire.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"}
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "check_eligibility",
                "description": "Starts the eligibility check workflow to determine program qualification.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"}
                    },
                    "required": ["user_id"]
                }
            }
        ]

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = data.get("message", "")
        user_id = data.get("user_id", "default")

        # 🛑 If user_id is None, fail early
        if not user_id:
            return self._format_response(False, "Missing user ID", {"error": "User ID is required."})

        # 🧠 Always check active session first
        current = self.user_sessions.get(user_id)
        if current == "diet":
            print("🔄 Routing to diet agent")
            response = self.diet_agent.process({"message": user_message, "user_id": user_id})
            if response.get("message") == "Assessment complete":
                self.user_sessions.pop(user_id, None)
            return response

        if current == "eligibility":
            print("🔄 Routing to eligibility agent")
            response = self.eligibility_agent.process({"message": user_message, "user_id": user_id})
            if response.get("message") == "Eligibility assessment complete":
                self.user_sessions.pop(user_id, None)
            return response

        # ✅ Now (only if not in session) call OpenAI function-calling...
        use_openai = os.getenv("USE_OPENAI", "true").lower() == "true"

        if use_openai:
            print("🧠 Calling OpenAI function-calling for PrimaryAssistant")
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_message},
                        {"role": "user", "content": f"User ID: {user_id}\nMessage: {user_message}"}
                    ],
                    functions=self.functions,
                    function_call="auto"
                )

                choice = response.choices[0]
                if choice.finish_reason == "function_call":
                    func_call = choice.message.function_call
                    function_name = func_call.name
                    arguments = json.loads(func_call.arguments)
                    called_user_id = arguments["user_id"]

                    if function_name == "start_diet_assessment":
                        print("✅ Starting diet assessment via function call")
                        self.user_sessions[called_user_id] = "diet"
                        return self.diet_agent.process({"message": "", "user_id": called_user_id})

                    elif function_name == "check_eligibility":
                        print("✅ Starting eligibility check via function call")
                        self.user_sessions[called_user_id] = "eligibility"
                        return self.eligibility_agent.process({"message": "", "user_id": called_user_id})

                else:
                    content = getattr(choice.message, 'content', None)
                    if not content:
                        content = "I'm here to assist with diet assessments, eligibility checks, or wellness guidance. How can I help you today?"
                    return self._format_response(True, "Response generated by GPT", {
                        "response": content
                    })

            except Exception as e:
                print(f"❌ Error using OpenAI function calling: {e}")
                return self._format_response(False, "OpenAI call failed", {
                    "error": str(e)
                })

        else:
            print("⚠️ Skipping OpenAI (USE_OPENAI is false)")
            return self._format_response(True, "Default reply", {
                "response": "I'm here to help, but OpenAI is currently disabled."
            })
