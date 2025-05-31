from typing import Dict, Any
from .base_agent import BaseAgent
from .dietary_assessment_agent import DietaryAssessmentAgent
from .user_agent import UserAgent
from .eligibility_agent import EligibilityAgent
import os
import json
import re

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
NO_KEYWORDS = ["no", "not now", "skip", "later", "not interested"]
YES_KEYWORDS = ["yes", "ok", "sure", "yeah", "yep", "let's go", "sounds good", "definitely", "absolutely", "of course"]

class PrimaryAssistant(BaseAgent):
    """Primary AI assistant that routes requests to specialized agents as needed, with guided nudges and context-aware positive response handling."""

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

        self.user_sessions = {}    # user_id -> 'diet', 'eligibility'
        self.user_progress = {}    # user_id -> { "onboarded": False, "skipped_onboarding": False, "diet_done": False, "eligibility_done": False }
        self.user_nudges = {}      # user_id -> last nudge type: 'save_email', 'diet', 'eligibility'

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

        if not user_id:
            return self._format_response(False, "Missing user ID", {"error": "User ID is required."})

        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "onboarded": False,
                "skipped_onboarding": False,
                "diet_done": False,
                "eligibility_done": False
            }

        progress = self.user_progress[user_id]
        nudged_this_turn = False

        # Check if user is mid-session
        current = self.user_sessions.get(user_id)
        if current == "diet":
            print("🔄 Routing to diet agent")
            response = self.diet_agent.process({"message": user_message, "user_id": user_id})
            if response.get("message") == "Assessment complete":
                self.user_sessions.pop(user_id, None)
                self.user_progress[user_id]["diet_done"] = True
            return response

        if current == "eligibility":
            print("🔄 Routing to eligibility agent")
            response = self.eligibility_agent.process({"message": user_message, "user_id": user_id})
            if response.get("message") == "Eligibility assessment complete":
                self.user_sessions.pop(user_id, None)
                self.user_progress[user_id]["eligibility_done"] = True
            return response

        # --- Smart detect positive response to nudges with context ---
        if self._is_positive_response(user_message):
            last_nudge = self.user_nudges.get(user_id)
            if last_nudge == "save_email":
                print("✅ Positive response detected — Asking for email input")
                return self._format_response(True, "Prompt Email", {
                    "response": "Great! Please type your email to get started."
                })
            if last_nudge == "diet":
                print("✅ Positive response detected — Starting Diet Assessment")
                self.user_sessions[user_id] = "diet"
                return self.diet_agent.process({"message": "", "user_id": user_id})
            if last_nudge == "eligibility":
                print("✅ Positive response detected — Starting Eligibility Check")
                self.user_sessions[user_id] = "eligibility"
                return self.eligibility_agent.process({"message": "", "user_id": user_id})

        # --- Email onboarding logic ---
        if not progress["onboarded"] and not progress["skipped_onboarding"]:
            message_lower = user_message.strip().lower()

            if re.match(EMAIL_REGEX, user_message.strip()):
                print(f"📧 Detected email {user_message.strip()}, onboarding user...")
                response = self.user_agent.process({"email": user_message.strip()})
                if response.get("success"):
                    self.user_progress[user_id]["onboarded"] = True
                    # ✅ Immediately send next nudge
                    next_nudge = self._check_for_nudge(user_id)
                    if next_nudge:
                        welcome_message = response.get("data", {}).get("response", "")
                        combined_response = f"{welcome_message}\n\n{next_nudge['data']['response']}"
                        return self._format_response(True, "Onboarding and Nudge", {
                            "response": combined_response
                        })
                return response

            elif any(kw in message_lower for kw in NO_KEYWORDS):
                print(f"🙅 User declined onboarding.")
                self.user_progress[user_id]["skipped_onboarding"] = True
                return self._nudge_next_step(user_id)

        # --- Nudge user based on progress first ---
        if not self.user_nudges.get(user_id):
            nudge_response = self._check_for_nudge(user_id)
            if nudge_response:
                nudged_this_turn = True
                return nudge_response

        # --- Let OpenAI handle any user input after nudging ---
        use_openai = os.getenv("USE_OPENAI", "true").lower() == "true"
        if use_openai:
            return self._handle_openai_fallback(user_message, user_id)

        # --- Fallback if OpenAI is disabled ---
        print("⚠️ Skipping OpenAI (USE_OPENAI is false)")
        return self._format_response(True, "Default reply", {
            "response": "I'm here to assist with diet assessments, eligibility checks, or wellness guidance. How can I help you today?"
        })

    def _is_positive_response(self, message: str) -> bool:
        """Detect positive user responses."""
        message_lower = message.strip().lower()
        return any(kw in message_lower for kw in YES_KEYWORDS)

    def _handle_openai_fallback(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """Let OpenAI decide what to do with user's message."""
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

    def _check_for_nudge(self, user_id: str) -> Dict[str, Any] | None:
        """Check if we need to nudge the user based on their progress."""
        progress = self.user_progress[user_id]
        if not progress["onboarded"] and not progress["skipped_onboarding"]:
            self.user_nudges[user_id] = "save_email"
            return self._format_response(True, "Nudge", {
                "response": "👋 Hey there! To personalize your experience, would you like to save your progress with an email?"
            })
        if not progress["diet_done"]:
            self.user_nudges[user_id] = "diet"
            return self._format_response(True, "Nudge", {
                "response": "🥦 Curious about your diet? Let's run a quick Diet Assessment to give you a snapshot!"
            })
        if not progress["eligibility_done"]:
            self.user_nudges[user_id] = "eligibility"
            return self._format_response(True, "Nudge", {
                "response": "📋 Ready to check if you're eligible for some amazing wellness programs? I can guide you!"
            })

        # ✅ If everything is done, no more nudging — send a "You're all set!" message
        self.user_nudges[user_id] = None
        return self._format_response(True, "Idle", {
            "response": "🎉 You're all set! Feel free to ask me anything about health, diet, or wellness."
        })

    def _nudge_next_step(self, user_id: str) -> Dict[str, Any]:
        """Send the next nudge after skipping onboarding."""
        return self._check_for_nudge(user_id)
