import os
from typing import Dict, Any
from .base_agent import BaseAgent

class DietaryAssessmentAgent(BaseAgent):
    """Agent to guide users through the ACLM diet screener and compute their dietary score."""

    def __init__(self):
        super().__init__()
        self.system_prompt = """
You are the dietary assessment specialist for Wellchemy. Your job is to administer the ACLM Diet Screener (Version 1).

Instructions:
- Ask users the dietary frequency questions from the ACLM Diet Screener PDF one by one.
- After each user answer, ask the next question in order.
- At the end of all questions, convert the responses into scores using the ACLM Diet Scoring Summary:
    - Never = 0 times/week
    - Less than 1x/week = 0.5 times/week
    - 1-3x/week = 2 times/week
    - 4-6x/week = 5 times/week
    - 1-2x/day = 10.5 times/week
    - More than 3x/day = 21 times/week
- Sum all scores to compute the user's total dietary frequency score.
- Provide a clear and friendly summary of their results at the end.

Always use a supportive, clear tone. Clarify if the user provides an unclear response.
"""
        self.questions = self._load_questions_from_pdf()
        self.state = {}  # user_id -> {"index": int, "answers": [float]}

    def _load_questions_from_pdf(self) -> list:
        """
        Return hardcoded dietary questions for the assessment.
        """
        lead_in = "Over the last four weeks, how often did you eat or drink the following items?"
        questions = [
            f"{lead_in} Whole grains (e.g., brown rice, whole wheat bread, oatmeal)?",
            "Vegetables (excluding potatoes)?",
            "Fruits?",
            "Legumes (beans, lentils, chickpeas)?",
            "Nuts and seeds?",
            "Processed meats (e.g., bacon, sausage, deli meats)?",
            "Red meat (beef, pork, lamb)?",
            "Fish and seafood?",
            "Dairy products?",
            "Eggs?",
            "Added sugars (e.g., candy, cookies, sugary drinks)?",
            "Fried foods?"
        ]
        return questions

    def _convert_to_score(self, answer: str) -> float:
        """Maps user response text to a numeric score."""
        score_map = {
            "never": 0,
            "less than 1x/week": 0.5,
            "1-3x/week": 2,
            "4-6x/week": 5,
            "1-2x/day": 10.5,
            "more than 3x/day": 21
        }
        normalized = answer.strip().lower()
        for key in score_map:
            if key in normalized:
                return score_map[key]
        return 0  # fallback for unrecognized input

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Drives the assessment session with scoring logic."""
        user_id = input_data.get("user_id", "default")
        message = input_data.get("message", "").strip()

        if user_id not in self.state:
            self.state[user_id] = {"index": 0, "answers": []}
            return self._format_response(True, "Starting diet assessment", {
                "response": f"{self.questions[0]}"
            })

        user_state = self.state[user_id]

        # Store the last answer
        if user_state["index"] < len(self.questions):
            score = self._convert_to_score(message)
            user_state["answers"].append(score)
            user_state["index"] += 1

        # Finish if last question answered
        if user_state["index"] >= len(self.questions):
            total_score = sum(user_state["answers"])
            max_score = len(user_state["answers"]) * 21
            percent = (total_score / max_score) * 100 if max_score else 0
            del self.state[user_id]

            return self._format_response(True, "Assessment complete", {
                "total_score": round(total_score, 1),
                "max_score": max_score,
                "percent": round(percent, 1),
                "response": f"Your dietary frequency score is {round(total_score,1)} out of {max_score} "
                            f"({round(percent,1)}%). Thank you for completing the assessment!"
            })

        # Ask the next question
        next_question = self.questions[user_state["index"]]
        return self._format_response(True, "Next question", {"response": next_question})
