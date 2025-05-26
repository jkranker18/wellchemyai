import os
from typing import Dict, Any
from .base_agent import BaseAgent
from PyPDF2 import PdfReader

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
        Returns only the main diet screener questions (categories),
        with optional examples as metadata.
        """
        return [
            {"question": "Fruit", "examples": "e.g., apples, bananas, berries, citrus, mangoes"},
            {"question": "Leafy green vegetables", "examples": "e.g., kale, spinach, lettuce"},
            {"question": "Other vegetables or vegetable dishes", "examples": "e.g., carrots, broccoli, mushrooms"},
            {"question": "Whole grains or whole grain products", "examples": "e.g., brown rice, whole wheat bread, oats"},
            {"question": "Refined grains or refined grain products", "examples": "e.g., white bread, white rice, pasta"},
            {"question": "Beans/legumes or products made from them", "examples": "e.g., black beans, chickpeas, lentils"},
            {"question": "Nuts, nut butters, seeds, avocado, or coconut", "examples": "e.g., almonds, flax, tahini"},
            {"question": "Meat or poultry or meat-based dishes", "examples": "e.g., beef, chicken, deli meat"},
            {"question": "Fish or shellfish or seafood-based dishes", "examples": "e.g., tuna, shrimp, salmon"},
            {"question": "Eggs or egg-based dishes", "examples": "e.g., omelet, hard-boiled eggs"},
            {"question": "Dairy milk", "examples": "e.g., skim, whole, chocolate milk"},
            {"question": "Other dairy foods", "examples": "e.g., cheese, yogurt, butter"},
            {"question": "Plant-based meat/mock meat or dairy alternatives", "examples": "e.g., tofu, plant-based burgers"},
            {"question": "Packaged/prepared foods or frozen meals", "examples": "e.g., frozen dinners, boxed mac & cheese"},
            {"question": "Restaurant/takeout foods", "examples": "e.g., fast food, takeout meals"},
            {"question": "Fast foods", "examples": "e.g., burgers and fries, fried chicken"},
            {"question": "Packaged bars, shakes, or powders", "examples": "e.g., protein bars, meal replacement shakes"},
            {"question": "Salty snacks or foods with added salt", "examples": "e.g., chips, pickles, salted nuts"},
            {"question": "Sweetened foods or foods with added sugar", "examples": "e.g., cookies, candy, soda"},
            {"question": "Fried foods or foods with added butter, fats, or oil", "examples": "e.g., fries, tempura"},
            {"question": "Water or plain herbal beverages", "examples": "e.g., plain water, herbal tea"},
            {"question": "Non-dairy milk", "examples": "e.g., almond, soy, oat milk"},
            {"question": "100% juice (fruit or vegetable)", "examples": "e.g., orange juice, beet juice"},
            {"question": "Beverages with added sugars/sweeteners", "examples": "e.g., soda, sweetened coffee"},
            {"question": "Coffee or other caffeinated beverages", "examples": "e.g., espresso, black tea"},
            {"question": "Alcoholic beverages", "examples": "e.g., wine, beer, liquor"},
        ]

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
        """Handles step-by-step assessment and scoring unless the user asks something unrelated."""
        user_id = input_data.get("user_id", "default")
        message = input_data.get("message", "").strip().lower()

        if user_id not in self.state:
            self.state[user_id] = {"index": 0, "answers": []}
            return self._format_response(True, "Starting diet assessment", {
                "response": f"Over the last four weeks, how often did you eat or drink: {self.questions[0]['question']}?"
            })

        user_state = self.state[user_id]
        current_q = self.questions[user_state["index"]]

        def is_frequency_response(msg: str) -> bool:
            freq_keywords = [
                "never", "less than", "1-3", "4-6", "1-2", "more than", "times", "per", "week", "day", "x"
            ]
            return any(k in msg for k in freq_keywords) or msg.replace(".", "").isdigit()

        # If the message looks like a frequency value, treat it as an answer
        if is_frequency_response(message) and user_state["index"] < len(self.questions):
            score = self._convert_to_score(message)
            user_state["answers"].append(score)
            user_state["index"] += 1

            # Check if done
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

            # Continue with next question
            next_q = self.questions[user_state["index"]]
            return self._format_response(True, "Next question", {
                "response": f"How often did you eat or drink: {next_q['question']}?"
            })

        # If message doesn't look like a frequency, provide clarification
        if "clarify" in message or "example" in message or "what" in message:
            return self._format_response(True, "Clarification", {
                "response": f"Here are some examples: {current_q['examples']}"
            })

        # If message does not look like a frequency and isn't asking for clarification, exit assessment flow
        del self.state[user_id]
        return self._format_response(True, "Exiting assessment", {
            "response": "Got it! If you'd like to continue the diet assessment later, just say so."
        })
