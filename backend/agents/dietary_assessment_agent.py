import os
from typing import Dict, Any
from .base_agent import BaseAgent
from db_connection import SessionLocal
from models import DietAssessment
from datetime import datetime

class DietaryAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = """
You are the dietary assessment specialist for Wellchemy. You guide users through the ACLM Diet Screener and compute scores.
"""
        self.questions = self._load_questions_from_pdf()
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
            return self._format_response(True, "Starting diet assessment", {
                "response": f"Over the last 4 weeks, how often did you eat or drink: {self.questions[0]['question']}?"
            })

        user_state = self.state[user_id]
        index = user_state["index"]

        if index < len(self.questions):
            score = self._convert_to_score(message)
            question_key = self.questions[index]["question"]
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

            db = SessionLocal()
            try:
                assessment = DietAssessment(
                    user_id=user_id,
                    question_scores=answers,
                    total_score=total_score,
                    max_score=max_score,
                    percent=percent
                )
                db.add(assessment)
                db.commit()
            finally:
                db.close()

            del self.state[user_id]

            return self._format_response(True, "Assessment complete", {
                "total_score": round(total_score, 1),
                "max_score": max_score,
                "percent": percent,
                "plant_food_score": plant_food_score,
                "water_score": water_score,
                "response": (
                    f"Assessment complete!\n"
                    f"🌿 Whole & Plant Food Frequency Score: {plant_food_score}%\n"
                    f"💧 Water & Herbal Beverages Score: {water_score}%"
                )
            })

        next_q = self.questions[user_state["index"]]
        return self._format_response(True, "Next question", {
            "response": f"How often did you eat or drink: {next_q['question']}?"
        })
