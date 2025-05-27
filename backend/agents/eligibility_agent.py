from typing import Dict, Any
from .base_agent import BaseAgent
from db_connection import SessionLocal
from models import EligibilityAssessment
from datetime import datetime

class EligibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = """
You are the eligibility assessment specialist for Wellchemy.
You ask a series of questions to determine if a user qualifies for a program.
"""
        self.questions = [
            {"key": "zip", "question": "What is your zip code?"},
            {"key": "insurance_provider", "question": "Who is your insurance provider?"},
            {"key": "chronic_conditions", "question": "Do you have any chronic conditions? (See: https://www.cdc.gov/chronic-disease/data-surveillance/index.html)"},
            {"key": "dietary_restrictions", "question": "Do you have any dietary restrictions? (See: https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies)"},
        ]
        self.branch_questions = {
            "abc insurance": [
                {"key": "abc_member_number", "question": "What is your ABC member number?"},
            ],
            "health insurance": [
                {"key": "pcp", "question": "Who is your Primary Care Physician?"},
                {"key": "medications_per_day", "question": "How many medications do you take per day?"},
            ]
        }
        self.questions.append({"key": "address", "question": "What is your address so we can be ready when approved?"})
        self.state = {}  # user_id -> {index, answers, branch_added}

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = input_data.get("user_id", "default")
        message = input_data.get("message", "").strip()

        if user_id not in self.state:
            self.state[user_id] = {"index": 0, "answers": {}, "branch_added": False}
            return self._format_response(True, "Starting eligibility assessment", {
                "response": self.questions[0]["question"]
            })

        user_state = self.state[user_id]
        idx = user_state["index"]

        # Clarification intent
        clarification_keywords = ["example", "what is", "explain", "what's that", "huh"]
        if any(k in message.lower() for k in clarification_keywords):
            question = self.questions[idx - 1]["question"]
            return self._format_response(True, "Clarification", {"response": f"Sure, here's more info: {question}"})

        # Record previous answer
        if idx > 0:
            prev_key = self.questions[idx - 1]["key"]
            user_state["answers"][prev_key] = message

        # Inject branch questions if needed
        if not user_state["branch_added"] and self.questions[idx - 1]["key"] == "insurance_provider":
            provider = message.lower()
            if provider in self.branch_questions:
                self.questions[idx:idx] = self.branch_questions[provider]
                user_state["branch_added"] = True

        # Done?
        if idx >= len(self.questions):
            answers = user_state["answers"]
            db = SessionLocal()
            try:
                assessment = EligibilityAssessment(
                    user_id=user_id,
                    answers=answers,
                    date_taken=datetime.utcnow()
                )
                db.add(assessment)
                db.commit()
            finally:
                db.close()

            del self.state[user_id]
            return self._format_response(True, "Eligibility assessment complete", {
                "response": f"Thanks! We've recorded your information and will contact your provider. Here's what you told us: {answers}"
            })

        user_state["index"] += 1
        next_q = self.questions[user_state["index"] - 1]
        return self._format_response(True, "Next question", {"response": next_q["question"]}) 