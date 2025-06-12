from typing import Dict, Any
from .base_agent import BaseAgent
from .conversational_dietary_assessment_agent import ConversationalDietaryAssessmentAgent
from .user_agent import UserAgent
from .conversational_eligibility_agent import ConversationalEligibilityAgent
from .prescription_agent import PrescriptionAgent
import os
import json
import re

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
NO_KEYWORDS = ["no", "not now", "skip", "later", "not interested"]
YES_KEYWORDS = ["yes", "ok", "sure", "yeah", "yep", "let's go", "sounds good", "definitely", "absolutely", "of course"]

class PrimaryAssistant(BaseAgent):
    """Primary AI assistant that routes requests to specialized agents as needed, with flow suggestions embedded in AI responses."""

    def __init__(self):
        super().__init__()
        
        # Load data files from the data directory
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Load programs
        with open(os.path.join(data_dir, "programs.json")) as f:
            self.programs = json.load(f)
            
        # Load chronic condition mapping
        with open(os.path.join(data_dir, "chronic_condition_diet_mapping.json")) as f:
            self.chronic_condition_diet_mapping = json.load(f)
            
        # Initialize agents
        self.dietary_assessment_agent = ConversationalDietaryAssessmentAgent()
        self.eligibility_agent = ConversationalEligibilityAgent()
        self.prescription_agent = PrescriptionAgent(self.programs, self.chronic_condition_diet_mapping)
        self.user_agent = UserAgent()

        self.user_sessions = {}    # user_id -> 'diet', 'eligibility'
        self.user_progress = {}    # user_id -> { "onboarded": False, "skipped_onboarding": False, "diet_done": False, "eligibility_done": False }

        self.functions = [
            {
                "name": "start_diet_assessment",
                "description": "Starts the conversational diet screener questionnaire.",
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

        if "prescription" in user_message.lower():
            print("💊 Prescription keyword detected — generating prescription...")
            # For now, hardcode a sample diet and eligibility assessment
            diet_assessment = {
                "vegetarian": True
            }
            eligibility_assessment = {
                "chronic_conditions": ["Hypertension"],
                "dietary_restrictions": ["shellfish"]
            }
            try:
                orders = self.prescription_agent.generate_prescription(user_id, diet_assessment, eligibility_assessment)
                # Format the orders nicely
                response_text = "✅ **Prescription Orders Generated!**\n\n"
                for i, order in enumerate(orders, 1):
                    meals_list = ', '.join(order['meals'])
                    response_text += (
                        f"📦 **Order {i}**\n"
                        f"- Delivery Date: **{order['delivery_date']}**\n"
                        f"- Meals: {meals_list}\n\n"
                    )
                return self._format_response(True, "Prescription Generated", {
                    "response": response_text
                }, user_id=user_id)
            except Exception as e:
                return self._format_response(False, "Error generating prescription", {
                    "error": str(e)
                }, user_id=user_id)

        # Return a default welcome message if the user message is 'start' or empty
        if user_message.strip().lower() in {"start", ""}:
            return self._format_response(True, "Welcome", {
                "response": (
                    "👋 Welcome to Wellchemy — a food as medicine platform powered by AI. "
                    "We assess your health, prescribe medically tailored meals, connect you to wellness programs, "
                    "answer any health related questions and help set you on a path to a healthier life.\n"
                    "Ready to get started?"
                )
            }, user_id=user_id)

        if not user_id:
            return self._format_response(False, "Missing user ID", {"error": "User ID is required."}, user_id=user_id)

        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "onboarded": False,
                "skipped_onboarding": False,
                "diet_done": False,
                "eligibility_done": False
            }

        progress = self.user_progress[user_id]

        # Check if user is mid-session
        current = self.user_sessions.get(user_id)
        if current == "diet":
            print("🔄 Routing to conversational diet agent")
            response = self.dietary_assessment_agent.process({"message": user_message, "user_id": user_id})
            if response.get("success") and response.get("message") == "Assessment complete":
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

        # --- Detect positive response to flow suggestion ---
        if self._is_positive_response(user_message):
            if not progress["diet_done"]:
                print("✅ Positive response detected — Starting Diet Assessment")
                self.user_sessions[user_id] = "diet"
                return self.dietary_assessment_agent.process({"message": "", "user_id": user_id})
            if not progress["eligibility_done"]:
                print("✅ Positive response detected — Starting Eligibility Check")
                self.user_sessions[user_id] = "eligibility"
                return self.eligibility_agent.process({"message": "", "user_id": user_id})

        # --- Handle email onboarding logic ---
        if not progress["onboarded"] and not progress["skipped_onboarding"]:
            message_lower = user_message.strip().lower()

            if re.match(EMAIL_REGEX, user_message.strip()):
                print(f"📧 Detected email {user_message.strip()}, onboarding user...")
                response = self.user_agent.process({"email": user_message.strip()})
                if response.get("success"):
                    self.user_progress[user_id]["onboarded"] = True
                    return self._format_response(True, "Onboarding", {
                        "response": response.get("data", {}).get("response", "Welcome!")
                    }, user_id=user_id)
                return response

            elif any(kw in message_lower for kw in NO_KEYWORDS):
                print(f"🙅 User declined onboarding.")
                self.user_progress[user_id]["skipped_onboarding"] = True

        # --- Proceed to OpenAI with progress-aware nudging inside system prompt ---
        use_openai = os.getenv("USE_OPENAI", "true").lower() == "true"
        if use_openai:
            return self._handle_openai_fallback(user_message, user_id, progress)

        print("⚠️ Skipping OpenAI (USE_OPENAI is false)")
        return self._format_response(True, "Default reply", {
            "response": "I'm here to assist with diet assessments, eligibility checks, or wellness guidance. How can I help you today?"
        }, user_id=user_id)

    def _is_positive_response(self, message: str) -> bool:
        message_lower = message.strip().lower()
        return any(kw in message_lower for kw in YES_KEYWORDS)

    def _handle_openai_fallback(self, user_message: str, user_id: str, progress: Dict[str, bool]) -> Dict[str, Any]:
        """Let OpenAI decide what to do with user's message, with progress-aware nudging."""
        try:
            system_prompt = f"""
You are the primary AI assistant for Wellchemy.
Your job is to help users with diet assessments, eligibility checks, and general wellness advice.

Here is the user's progress:
- Email collected: {"✅" if progress.get("onboarded") or progress.get("skipped_onboarding") else "❌"}
- Diet Assessment completed: {"✅" if progress.get("diet_done") else "❌"}
- Eligibility Check completed: {"✅" if progress.get("eligibility_done") else "❌"}

If the user hasn't completed a Diet Assessment or Eligibility Check, you can suggest it casually after answering their question.

Remember:
- Always answer the user's question first.
- Then, if appropriate, gently suggest a next step (Diet Assessment or Eligibility Check).
- Be helpful, professional, and conversational.
            """

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
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
                    return self.dietary_assessment_agent.process({"message": "", "user_id": called_user_id})

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
                }, user_id=user_id)

        except Exception as e:
            print(f"❌ Error using OpenAI function calling: {e}")
            return self._format_response(False, "OpenAI call failed", {
                "error": str(e)
            }, user_id=user_id)
