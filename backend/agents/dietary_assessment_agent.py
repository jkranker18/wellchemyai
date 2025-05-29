import os
from typing import Dict, Any
from .base_agent import BaseAgent

class DietaryAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = """
You are the dietary assessment specialist for Wellchemy. You guide users through the ACLM Diet Screener and compute scores.
"""
        self.questions = self._load_questions_from_pdf()
        self.examples = {
            "Fruit": "e.g., apples, bananas, pears",
            "Whole grains or whole grain products": "e.g., quinoa, millet, barley",
            "Leafy green vegetables": "e.g., spinach, kale, romaine",
            "Other vegetables or vegetable dishes": "e.g., carrots, broccoli, zucchini",
            "Beans/legumes or products made from them": "e.g., black beans, chickpeas, lentils",
            "Nuts, nut butters, seeds, avocado, or coconut": "e.g., almonds, walnuts, chia seeds",
            "Meat or poultry or meat-based dishes": "e.g., chicken, beef, pork",
            "Fish or shellfish or seafood-based dishes": "e.g., salmon, shrimp, tuna",
            "Eggs or egg-based dishes": "e.g., scrambled eggs, omelets",
            "Dairy milk": "e.g., whole milk, skim milk",
            "Other dairy foods": "e.g., cheese, yogurt",
            "Plant-based meat/mock meat or dairy alternatives": "e.g., tofu, soy milk",
            "Packaged/prepared foods or frozen meals": "e.g., TV dinners, microwaveable meals",
            "Restaurant/takeout foods": "e.g., fast food, pizza",
            "Fast foods": "e.g., burgers, fries",
            "Packaged bars, shakes, or powders": "e.g., protein bars, meal shakes",
            "Salty snacks or foods with added salt": "e.g., chips, pretzels",
            "Sweetened foods or foods with added sugar": "e.g., cookies, cake",
            "Fried foods or foods with added butter, fats, or oil": "e.g., fried chicken, tempura",
            "Water or plain herbal beverages": "e.g., water, chamomile tea",
            "Non-dairy milk": "e.g., almond milk, oat milk",
            "100% juice (fruit or vegetable)": "e.g., orange juice, beet juice",
            "Beverages with added sugars/sweeteners": "e.g., soda, sweetened iced tea",
            "Coffee or other caffeinated beverages": "e.g., coffee, energy drinks",
            "Alcoholic beverages": "e.g., beer, wine, whiskey"
        }
        self.state = {}  # user_id -> {"index": int, "answers": Dict[str, float]}

    def _load_questions_from_pdf(self) -> list:
        return [
            {"question": "Fruit"},
            {"question": "Leafy green vegetables"},
            {"question": "Other vegetables or vegetable dishes"},
            {"question": "Whole grains or whole grain products"},
            {"question": "Refined grains or refined grain products"},
            {"question": "Beans/legumes or products made from them"},
            {"question": "Nuts, nut butters, seeds, avocado, or coconut"},
            {"question": "Meat or poultry or meat-based dishes"},
            {"question": "Fish or shellfish or seafood-based dishes"},
            {"question": "Eggs or egg-based dishes"},
            {"question": "Dairy milk"},
            {"question": "Other dairy foods"},
            {"question": "Plant-based meat/mock meat or dairy alternatives"},
            {"question": "Packaged/prepared foods or frozen meals"},
            {"question": "Restaurant/takeout foods"},
            {"question": "Fast foods"},
            {"question": "Packaged bars, shakes, or powders"},
            {"question": "Salty snacks or foods with added salt"},
            {"question": "Sweetened foods or foods with added sugar"},
            {"question": "Fried foods or foods with added butter, fats, or oil"},
            {"question": "Water or plain herbal beverages"},
            {"question": "Non-dairy milk"},
            {"question": "100% juice (fruit or vegetable)"},
            {"question": "Beverages with added sugars/sweeteners"},
            {"question": "Coffee or other caffeinated beverages"},
            {"question": "Alcoholic beverages"}
        ]

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

        try:
            value = float(normalized)
            if value == 0:
                return 0
            elif value < 1:
                return 0.5
            elif value < 4:
                return 2
            elif value < 7:
                return 5
            elif value < 15:
                return 10.5
            else:
                return 21
        except ValueError:
            return 0

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = input_data.get("user_id", "default")
        message = input_data.get("message", "").strip()

        if user_id not in self.state:
            self.state[user_id] = {"index": 0, "answers": {}}
            next_q = self.questions[0]["question"]
            drink_items = {
                "Water or plain herbal beverages",
                "Non-dairy milk",
                "100% juice (fruit or vegetable)",
                "Beverages with added sugars/sweeteners",
                "Coffee or other caffeinated beverages",
                "Alcoholic beverages",
                "Dairy milk"
            }
            verb = "drink" if next_q in drink_items else "eat"
            return self._format_response(True, "Starting diet assessment", {
                "response": f"Over the last 4 weeks, how often did you {verb}: {next_q}?"
            })

        user_state = self.state[user_id]
        index = user_state["index"]

        if index < len(self.questions):
            question_key = self.questions[index]["question"]

            if any(kw in message.lower() for kw in [
                "example", "what is", "explain", "what's that", "huh", "can you give me an example"
            ]):
                example_text = self.examples.get(question_key)
                if example_text:
                    return self._format_response(True, "Clarification", {
                        "response": f"Some examples of {question_key.lower()} include: {example_text}"
                    })

            score = self._convert_to_score(message)
            user_state["answers"][question_key] = score
            user_state["index"] += 1

            if user_state["index"] >= len(self.questions):
                answers = user_state["answers"]

                whole_plant_foods = {
                    "Fruit", "Leafy green vegetables", "Other vegetables or vegetable dishes",
                    "Whole grains or whole grain products", "Beans/legumes or products made from them",
                    "Nuts, nut butters, seeds, avocado, or coconut"
                }

                beverage_items = {
                    "Water or plain herbal beverages", "Non-dairy milk", "100% juice (fruit or vegetable)",
                    "Beverages with added sugars/sweeteners", "Coffee or other caffeinated beverages", "Alcoholic beverages"
                }

                food_items_total = sum(v for k, v in answers.items() if k not in beverage_items)
                plant_food_total = sum(answers.get(k, 0) for k in whole_plant_foods)
                beverage_total = sum(answers.get(k, 0) for k in beverage_items)

                plant_food_score = round((plant_food_total / food_items_total) * 100, 1) if food_items_total else 0
                water_score = round((answers.get("Water or plain herbal beverages", 0) / beverage_total) * 100, 1) if beverage_total else 0

                total_score = sum(answers.values())
                max_score = len(answers) * 21
                percent = round((total_score / max_score) * 100, 1) if max_score else 0
                gdqs_equivalent = (total_score / max_score) * 40 if max_score else 0

                # Determine risk tier based on GDQS-style thresholds
                if gdqs_equivalent < 15:
                    risk_level = "high risk"
                elif gdqs_equivalent < 23:
                    risk_level = "moderate risk"
                else:
                    risk_level = "low risk"

                del self.state[user_id]

                assessment_response = (
                    f"🌿 Whole & Plant Food Frequency Score: {plant_food_score}%\n"
                    f"\n"
                    f"💧 Water & Herbal Beverages Score: {water_score}%\n"
                    f"\n"
                    f"Based on your dietary frequency score of {round(total_score, 1)}, "
                    f"this equates to a **{risk_level}** dietary pattern using Global Diet Quality Score categories.\n"
                    f"\n"
                    f"Now that we know that, we're here to help you make healthier choices."
                )

                return self._format_response(True, "Assessment complete", {
                    "response": assessment_response
                })

            next_q = self.questions[user_state["index"]]["question"]
            drink_items = {
                "Water or plain herbal beverages",
                "Non-dairy milk",
                "100% juice (fruit or vegetable)",
                "Beverages with added sugars/sweeteners",
                "Coffee or other caffeinated beverages",
                "Alcoholic beverages",
                "Dairy milk"
            }
            verb = "drink" if next_q in drink_items else "eat"
            return self._format_response(True, "Next question", {
                "response": f"Over the last 4 weeks, how often did you {verb}: {next_q}?"
            })

