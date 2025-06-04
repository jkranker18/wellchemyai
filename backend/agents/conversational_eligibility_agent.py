import os
import random
import json
from typing import Dict, Any
from .base_agent import BaseAgent
from db_connection import SessionLocal
from models import EligibilityAssessment, User
from datetime import datetime
import traceback
import uuid

class ConversationalEligibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__()

        self.questions = [
            {"key": "zip", "question": "What is your zip code?"},
            {"key": "insurance_provider", "question": "Who is your health insurance provider?"}
        ]

        self.branch_questions = {
            "abc": [
                {"key": "abc_member_id", "question": "What is your ABC member ID?"},
                {"key": "hospital_visits", "question": "How many times have you been to the hospital in the past 6 months?"}
            ],
            "florida blue": [
                {"key": "florida_blue_member_id", "question": "What is your Florida Blue member ID number?"},
                {"key": "medications_per_day", "question": "How many medications are you currently taking per day?"}
            ]
        }

        self.unbranch_questions = [
            {"key": "chronic_conditions", "question": "Please list any and all chronic conditions you currently have. (e.g., high blood pressure, diabetes, cancer)"},
            {"key": "dietary_restrictions", "question": "Please list any and all dietary restrictions you currently have. (e.g., shellfish, tree nuts)"},
            {"key": "delivery_address", "question": "What is your delivery address so we can be ready to send your food as soon as you are approved?"}
        ]

        self.state = {}  # user_id -> {stage, index, answers, branch}
        self.chronic_conditions_url = "https://www.cdc.gov/chronicdisease/resources/publications/factsheets.htm"
        self.dietary_restrictions_url = "https://www.foodallergy.org/living-food-allergies/food-allergy-essentials/common-allergens"

        self.instruction_styles = [
            "Ask this question in a warm, casual way.",
            "Ask this question politely and friendly, without sounding formal.",
            "Rephrase the question naturally and conversationally.",
            "Ask the question casually, like a helpful guide.",
            "Pose the question in a friendly, relaxed way.",
            "Ask this question as if you're a supportive coach.",
            "Ask the question in a positive and inviting tone.",
            "Frame the question in a caring and conversational style.",
            "Ask casually, but remain professional and clear.",
            "Pose the question in a naturally flowing way, like a conversation."
        ]

    def _create_guest_user(self) -> int:
        db = SessionLocal()
        try:
            print("Creating guest user...")
            guest_user = User(
                email=f"guest_{uuid.uuid4()}@wellchemy.ai",
                password_hash="auto-created",
                first_login=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.add(guest_user)
            db.commit()
            db.refresh(guest_user)
            print(f"Guest user created with ID: {guest_user.user_id}")
            return guest_user.user_id
        except Exception as e:
            print(f"Error creating guest user: {str(e)}\n{traceback.format_exc()}")
            db.rollback()
            raise
        finally:
            db.close()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = input_data.get("user_id", "default")
        message = input_data.get("message", "").strip()

        if user_id == "default" or user_id is None:
            user_id = self._create_guest_user()

        if user_id not in self.state:
            self.state[user_id] = {
                "stage": "initial",
                "index": 0,
                "answers": {},
                "branch": None
            }

        user_state = self.state[user_id]
        stage = user_state["stage"]
        index = user_state["index"]

        if any(kw in message.lower() for kw in ["example", "like what", "what is", "explain", "what's that", "huh", "help"]):
            if stage == "unbranch" and index == 0:
                return self._format_response(True, "Clarification", {
                    "response": f"Sure! Here's a helpful resource on chronic conditions: {self.chronic_conditions_url}"
                })
            if stage == "unbranch" and index == 1:
                return self._format_response(True, "Clarification", {
                    "response": f"Sure! Here's a helpful resource on common dietary restrictions: {self.dietary_restrictions_url}"
                })

        if stage == "initial":
            if index < len(self.questions):
                user_state["answers"][self.questions[index]["key"]] = message
                index += 1
                user_state["index"] = index

                if index == len(self.questions):
                    provider = user_state["answers"]["insurance_provider"].strip().lower()
                    if provider in self.branch_questions:
                        user_state["stage"] = "branch"
                        user_state["index"] = 0
                        user_state["branch"] = provider
                    else:
                        user_state["stage"] = "unbranch"
                        user_state["index"] = 0
            return self._next_question(user_id)

        if stage == "branch":
            branch = user_state["branch"]
            branch_qs = self.branch_questions[branch]

            if index < len(branch_qs):
                user_state["answers"][branch_qs[index]["key"]] = message
                index += 1
                user_state["index"] = index

                if index == len(branch_qs):
                    user_state["stage"] = "unbranch"
                    user_state["index"] = 0
            return self._next_question(user_id)

        if stage == "unbranch":
            if index < len(self.unbranch_questions):
                user_state["answers"][self.unbranch_questions[index]["key"]] = message
                index += 1
                user_state["index"] = index

                if index == len(self.unbranch_questions):
                    return self._save_and_finish(user_id, user_state["answers"])
            return self._next_question(user_id)

        return self._format_response(False, "No active session.")

    def _next_question(self, user_id: str) -> Dict[str, Any]:
        user_state = self.state[user_id]
        stage = user_state["stage"]
        index = user_state["index"]

        if stage == "initial" and index < len(self.questions):
            question = self.questions[index]["question"]
        elif stage == "branch":
            branch = user_state["branch"]
            branch_qs = self.branch_questions[branch]
            question = branch_qs[index]["question"]
        elif stage == "unbranch":
            question = self.unbranch_questions[index]["question"]
        else:
            return self._format_response(False, "No questions left.")

        style_instruction = random.choice(self.instruction_styles)

        system_prompt = f"""
You are a professional but friendly Eligibility Assessment Assistant for Wellchemy.

{style_instruction}

Do not skip or change the question meaning.

Here is the next question you must ask:

"{question}"
""".strip()

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Ask the next question, please."}
                ]
            )

            ai_message = response.choices[0].message.content

            return self._format_response(True, "Next question", {
                "response": ai_message
            })

        except Exception as e:
            print(f"Error generating next question: {e}")
            return self._format_response(False, "Error", {"error": str(e)})

    def _save_and_finish(self, user_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            print(f"Saving eligibility assessment for user {user_id}")
            record = EligibilityAssessment(
                user_id=user_id,
                answers=json.dumps(answers),
                date_taken=datetime.utcnow()
            )
            db.add(record)
            db.commit()
            print("Eligibility assessment saved successfully")
        except Exception as e:
            print(f"Error saving eligibility assessment: {str(e)}\n{traceback.format_exc()}")
            db.rollback()
            raise
        finally:
            db.close()

        del self.state[user_id]

        formatted_answers = self._format_answers(answers)
        health_tip = self._generate_health_tip()

        final_message = (
            f"Thanks! We've recorded your information and will contact your provider for verification.\n"
            f"Here's what you told us:\n\n"
            f"{formatted_answers}\n\n"
            f"✅ We'll let you know as soon as you're approved. In the meantime, feel free to ask me anything about your diet, wellness, or health — I'm here to help!\n\n"
            f"🌟 **Health Tip:** {health_tip}"
        )

        return self._format_response(True, "Eligibility assessment complete", {
            "response": final_message
        })

    def _generate_health_tip(self) -> str:
        try:
            prompt = (
                "Give me one short and practical health tip. It can be about healthy eating, "
                "staying active, or supporting mental wellness. Keep it to 1-2 sentences. "
                "Make it friendly and motivating."
            )

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a wellness expert providing health advice."},
                    {"role": "user", "content": prompt}
                ],
                timeout=10
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ Error generating health tip: {e}")
            return "🌟 Here's a quick tip: Stay hydrated and move your body daily for better health!"

    def _format_answers(self, answers: Dict[str, Any]) -> str:
        return "\n".join(f"**{key.replace('_', ' ').title()}:** {value}" for key, value in answers.items())
