from typing import Dict, Any
from .base_agent import BaseAgent
from db_connection import SessionLocal
from models import EligibilityAssessment, User
from datetime import datetime
import traceback
import uuid

class EligibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = """
You are the eligibility assessment specialist for Wellchemy.
You ask a series of questions to determine if a user qualifies for a program. This should only take 1–2 minutes.
"""
        self.initial_prompt = (
            "Now we're going to collect a bit more information to see if you qualify for one of our programs. "
            "Some of these are health-related and some are location and insurance related. This should only take 1–2 minutes."
        )
        self.questions = [
            {"key": "zip", "question": "What is your zip code?"},
            {"key": "insurance_provider", "question": "Who is your health insurance provider?"},
        ]
        self.branch_questions = {
            "abc": [
                {"key": "abc_member_id", "question": "What is your ABC member ID?"},
                {"key": "hospital_visits", "question": "How many times have you been to the hospital in the past 6 months?"},
            ],
            "florida blue": [
                {"key": "florida_blue_member_id", "question": "What is your Florida Blue member ID number?"},
                {"key": "medications_per_day", "question": "How many medications are you currently taking per day?"},
            ]
        }
        self.unbranch_questions = [
            {"key": "chronic_conditions", "question": "Please list any and all chronic conditions you currently have. (for example - High blood pressure, diabetes, cancer)"},
            {"key": "dietary_restrictions", "question": "Please list any and all dietary restrictions you currently have. (for example - shellfish, or tree nuts)"},
            {"key": "delivery_address", "question": "Great! Now, what is your delivery address so we can be ready to send your food as soon as you are approved?"},
        ]
        self.state = {}  # user_id -> {index, answers, branch, stage}

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
        try:
            user_id = input_data.get("user_id", "default")
            message = input_data.get("message", "").strip()

            print(f"Processing eligibility request - User ID: {user_id}, Message: {message}")

            if user_id == "default" or user_id is None:
                if not self.state:
                    user_id = self._create_guest_user()
                else:
                    user_id = next(iter(self.state.keys()))

            if user_id not in self.state:
                self.state[user_id] = {
                    "index": 0,
                    "answers": {},
                    "branch": None,
                    "stage": "initial"
                }
                return self._format_response(True, "Starting eligibility assessment", {
                    "response": f"{self.initial_prompt}\n\n{self.questions[0]['question']}"
                })

            user_state = self.state[user_id]
            index = user_state["index"]
            stage = user_state["stage"]

            clarification_keywords = ["example", "what is", "explain", "what's that", "huh"]
            if any(k in message.lower() for k in clarification_keywords):
                last_q = self._get_last_question(user_state)
                return self._format_response(True, "Clarification", {"response": f"Sure! Here's that question again: {last_q}"})

            if stage == "initial" and index < len(self.questions):
                user_state["answers"][self.questions[index]["key"]] = message
                index += 1
                user_state["index"] = index
                if index == 2:
                    provider = user_state["answers"].get("insurance_provider", "").lower()
                    if provider in self.branch_questions:
                        user_state["branch"] = provider
                        user_state["stage"] = "branch"
                        user_state["index"] = 0
                        return self._format_response(True, "Next question", {"response": self.branch_questions[provider][0]["question"]})
                    else:
                        user_state["stage"] = "unbranch"
                        user_state["index"] = 0
                        return self._format_response(True, "Next question", {"response": self.unbranch_questions[0]["question"]})
                elif index < len(self.questions):
                    return self._format_response(True, "Next question", {"response": self.questions[index]["question"]})

            elif stage == "branch":
                branch = user_state["branch"]
                user_state["answers"][self.branch_questions[branch][index]["key"]] = message
                index += 1
                user_state["index"] = index
                if index >= len(self.branch_questions[branch]):
                    user_state["stage"] = "unbranch"
                    user_state["index"] = 0
                    return self._format_response(True, "Next question", {"response": self.unbranch_questions[0]["question"]})
                else:
                    return self._format_response(True, "Next question", {"response": self.branch_questions[branch][index]["question"]})

            elif stage == "unbranch":
                user_state["answers"][self.unbranch_questions[index]["key"]] = message
                index += 1
                user_state["index"] = index
                if index >= len(self.unbranch_questions):
                    answers = user_state["answers"]
                    db = SessionLocal()
                    try:
                        print(f"Saving eligibility assessment for user {user_id}")
                        record = EligibilityAssessment(
                            user_id=user_id,
                            answers=answers,
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

                    readable = "\n".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in answers.items()])
                    return self._format_response(True, "Eligibility assessment complete", {
                        "response": f"Thanks! We've recorded your information and will contact your provider.  We'll send you a welcome email as soon as you are apporved!\n\nHere is what you told us:\n{readable}"
                    })
                else:
                    return self._format_response(True, "Next question", {"response": self.unbranch_questions[index]["question"]})
        except Exception as e:
            error_msg = f"Error in eligibility agent: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return self._format_response(False, "Error", {"error": str(e)})

    def _get_last_question(self, user_state):
        stage = user_state["stage"]
        index = user_state["index"]
        if stage == "initial":
            return self.questions[max(index - 1, 0)]["question"]
        elif stage == "branch" and user_state["branch"]:
            return self.branch_questions[user_state["branch"]][max(index - 1, 0)]["question"]
        elif stage == "unbranch":
            return self.unbranch_questions[max(index - 1, 0)]["question"]
        return ""
