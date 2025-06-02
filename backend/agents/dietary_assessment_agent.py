from typing import Dict, Any
from .base_agent import BaseAgent
import json

class ConversationalDietaryAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__()

        self.categories = [
            "Fruit",
            "Leafy green vegetables",
            "Other vegetables or vegetable dishes",
            "Whole grains or whole grain products",
            "Refined grains or refined grain products",
            "Beans/legumes or products made from them",
            "Nuts, nut butters, seeds, avocado, or coconut",
            "Meat or poultry or meat-based dishes",
            "Fish or shellfish or seafood-based dishes",
            "Eggs or egg-based dishes",
            "Dairy milk",
            "Other dairy foods",
            "Plant-based meat/mock meat or dairy alternatives",
            "Packaged/prepared foods or frozen meals",
            "Restaurant/takeout foods",
            "Fast foods",
            "Packaged bars, shakes, or powders",
            "Salty snacks or foods with added salt",
            "Sweetened foods or foods with added sugar",
            "Fried foods or foods with added butter, fats, or oil",
            "Water or plain herbal beverages",
            "Non-dairy milk",
            "100% juice (fruit or vegetable)",
            "Beverages with added sugars/sweeteners",
            "Coffee or other caffeinated beverages",
            "Alcoholic beverages"
        ]

        self.state = {}  # user_id -> {answers: {}, collecting: True/False, current_category: int, welcomed: bool}

    def _normalize_frequency(self, freeform_answer: str) -> str:
        """Use OpenAI to normalize freeform answer to one of 6 categories."""
        messages = [
            {"role": "system", "content": "You are a frequency normalizer. Given a user's freeform description of how often they consume a food, convert it into one of: Never, Less than 1x/week, 1-3x/week, 4-6x/week, 1-2x/day, More than 3x/day. Only return the normalized option exactly."},
            {"role": "user", "content": freeform_answer}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        normalized = response.choices[0].message.content.strip()
        return normalized

    def _convert_to_score(self, answer: str) -> float:
        normalized = answer.strip().lower()

        score_map = {
            "never": 0,
            "less than 1x/week": 0.5,
            "1-3x/week": 2,
            "4-6x/week": 5,
            "1-2x/day": 10.5,
            "more than 3x/day": 21
        }
        for key in score_map:
            if key in normalized:
                return score_map[key]

        return -1  # Indicate invalid input

    def _calculate_scores(self, answers: Dict[str, str]) -> str:
        numeric_answers = {k: self._convert_to_score(v) for k, v in answers.items()}

        whole_plant_foods = {
            "Fruit", "Leafy green vegetables", "Other vegetables or vegetable dishes",
            "Whole grains or whole grain products", "Beans/legumes or products made from them",
            "Nuts, nut butters, seeds, avocado, or coconut"
        }

        beverage_items = {
            "Water or plain herbal beverages", "Non-dairy milk", "100% juice (fruit or vegetable)",
            "Beverages with added sugars/sweeteners", "Coffee or other caffeinated beverages", "Alcoholic beverages"
        }

        food_items_total = sum(v for k, v in numeric_answers.items() if v >= 0 and k not in beverage_items)
        plant_food_total = sum(numeric_answers.get(k, 0) for k in whole_plant_foods)
        beverage_total = sum(numeric_answers.get(k, 0) for k in beverage_items)

        plant_food_score = round((plant_food_total / food_items_total) * 100, 1) if food_items_total else 0
        water_score = round((numeric_answers.get("Water or plain herbal beverages", 0) / beverage_total) * 100, 1) if beverage_total else 0

        total_score = sum(v for v in numeric_answers.values() if v >= 0)
        max_score = len(numeric_answers) * 21
        percent = round((total_score / max_score) * 100, 1) if max_score else 0
        gdqs_equivalent = (total_score / max_score) * 40 if max_score else 0

        if gdqs_equivalent < 15:
            risk_level = "high risk"
        elif gdqs_equivalent < 23:
            risk_level = "moderate risk"
        else:
            risk_level = "low risk"

        final_message = (
            f"\n🌿 Whole & Plant Food Frequency Score: {percent}%\n"
            f"💧 Water & Herbal Beverages Score: {water_score}%\n"
            f"\nBased on your dietary frequency score of {round(total_score, 1)}, "
            f"this equates to a **{risk_level}** dietary pattern using Global Diet Quality Score categories.\n"
            f"\nNow that we know that, we're here to help you make healthier choices!"
        )

        return final_message

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = input_data.get("user_id", "default")
        message = input_data.get("message", "").strip()

        if user_id not in self.state:
            self.state[user_id] = {"answers": {}, "collecting": True, "current_category": 0, "welcomed": False}

        user_state = self.state[user_id]

        if not user_state["collecting"]:
            return self._format_response(False, "No active session.")

        # Welcome the user if not yet welcomed
        if not user_state["welcomed"]:
            user_state["welcomed"] = True
            welcome_message = (
                "Welcome to Wellchemy's Diet Assessment! We'll ask about your typical diet over the past 4 weeks.\n"
                "Please answer using approximate frequency like: Never, Less than 1x/week, 1-3x/week, 4-6x/week, 1-2x/day, More than 3x/day.\n"
                "Let's get started!\n"
            )
            next_category = self.categories[user_state["current_category"]]
            prompt = (
                f"Over the past 4 weeks, how often did you consume {next_category}?\n"
                f"Please answer freely, and I will interpret your answer."
            )
            return self._format_response(True, "Continue conversation", {"response": welcome_message + prompt})

        # Record the user's answer to the current question
        if message and user_state["current_category"] < len(self.categories):
            normalized_answer = self._normalize_frequency(message)
            score = self._convert_to_score(normalized_answer)

            if score == -1:
                # Invalid input
                next_category = self.categories[user_state["current_category"]]
                reprompt = (
                    f"I didn't quite catch that. Please answer using approximate terms like: Never, Less than 1x/week, 1-3x/week, 4-6x/week, 1-2x/day, More than 3x/day.\n"
                    f"How often did you consume {next_category}?"
                )
                return self._format_response(True, "Invalid input", {"response": reprompt})

            category = self.categories[user_state["current_category"]]
            user_state["answers"][category] = normalized_answer
            user_state["current_category"] += 1

        # Check if all questions are answered
        if user_state["current_category"] >= len(self.categories):
            user_state["collecting"] = False
            final_message = self._calculate_scores(user_state["answers"])
            del self.state[user_id]

            return self._format_response(True, "Assessment complete", {"response": final_message})

        # Otherwise ask next category
        next_category = self.categories[user_state["current_category"]]
        prompt = (
            f"Over the past 4 weeks, how often did you consume {next_category}?\n"
            f"Please answer freely, and I will interpret your answer."
        )

        return self._format_response(True, "Continue conversation", {"response": prompt})
