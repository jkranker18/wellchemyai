import os
import json
from typing import Dict, Any
from .base_agent import BaseAgent
from db_connection import SessionLocal
from models import DietAssessment, User
from datetime import datetime
import traceback
import uuid

class ConversationalDietaryAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__()

        self.state = {}  # user_id -> session state

        self.categories = [
            "Fruits",
            "Vegetables",
            "Whole Grains",
            "Legumes",
            "Nuts",
            "Water",
            "Herbal Beverages",
            "Sugar-sweetened Beverages",
            "Red Meat",
            "Processed Meat",
            "Fish",
            "Dairy",
            "Added Sugar",
            "Refined Grains",
            "Oils",
            "Fast Food",
            "Snacks",
            "Desserts",
            "Eggs",
            "Plant-based Dairy Alternatives",
            "Fermented Foods",
            "Green Tea",
            "Coffee",
            "Alcohol",
            "Artificial Sweeteners",
            "Fried Foods"
        ]

        self.food_examples = {
            "Fruits": "e.g., apples, bananas, oranges",
            "Vegetables": "e.g., spinach, carrots, broccoli",
            "Whole Grains": "e.g., brown rice, oatmeal, whole grain bread",
            "Legumes": "e.g., beans, lentils, chickpeas",
            "Nuts": "e.g., almonds, walnuts, cashews",
            "Water": "e.g., plain water, mineral water",
            "Herbal Beverages": "e.g., chamomile tea, peppermint tea",
            "Sugar-sweetened Beverages": "e.g., soda, sweetened iced tea",
            "Red Meat": "e.g., beef, lamb, pork",
            "Processed Meat": "e.g., bacon, sausages, deli meats",
            "Fish": "e.g., salmon, tuna, cod",
            "Dairy": "e.g., milk, cheese, yogurt",
            "Added Sugar": "e.g., candy, pastries, sugary cereals",
            "Refined Grains": "e.g., white bread, white rice, pasta",
            "Oils": "e.g., olive oil, canola oil, vegetable oil",
            "Fast Food": "e.g., burgers, fries, pizza",
            "Snacks": "e.g., chips, pretzels, granola bars",
            "Desserts": "e.g., cake, cookies, ice cream",
            "Eggs": "e.g., scrambled eggs, boiled eggs",
            "Plant-based Dairy Alternatives": "e.g., almond milk, soy yogurt",
            "Fermented Foods": "e.g., yogurt, kefir, sauerkraut",
            "Green Tea": "e.g., matcha, sencha",
            "Coffee": "e.g., black coffee, espresso",
            "Alcohol": "e.g., wine, beer, spirits",
            "Artificial Sweeteners": "e.g., diet soda, sugar-free gum",
            "Fried Foods": "e.g., fried chicken, tempura, onion rings"
        }

        self.response_map = {
            "every day": 7,
            "daily": 7,
            "most days": 5,
            "often": 5,
            "sometimes": 3,
            "occasionally": 2,
            "rarely": 1,
            "never": 0
        }

    def _create_guest_user(self) -> int:
        """Create a guest user and return their ID."""
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
        user_id = input_data.get("user_id")
        message = input_data.get("message", "").strip().lower()

        if user_id is None or user_id == "default":
            user_id = self._create_guest_user()
        else:
            user_id = int(user_id)

        if user_id not in self.state:
            # Initialize state
            self.state[user_id] = {
                "collecting": True,
                "current_category_index": 0,
                "answers": {}
            }

        session = self.state[user_id]

        if session["collecting"]:
            if session["current_category_index"] == 0 and message == "":
                # First time: ask about the first category
                return self._ask_next_category(user_id)

            # Save the user's response
            current_category = self.categories[session["current_category_index"]]
            estimated_frequency = self._estimate_frequency(message)
            session["answers"][current_category] = estimated_frequency

            session["current_category_index"] += 1

            if session["current_category_index"] >= len(self.categories):
                # Done!
                session["collecting"] = False
                return self._save_and_finish(user_id, session["answers"])

            # Ask about the next category
            return self._ask_next_category(user_id)

        return self._format_response(False, "No active session.")

    def _estimate_frequency(self, user_response: str) -> int:
        """Estimate frequency based on user's response."""
        for key_phrase, frequency in self.response_map.items():
            if key_phrase in user_response:
                return frequency

        # Default fallback if no keyword matched
        try:
            # Maybe the user typed a number
            number = int(user_response)
            return max(0, min(7, number))
        except:
            # If we can’t parse anything, assume occasional (3)
            return 3

    def _ask_next_category(self, user_id: str) -> Dict[str, Any]:
        session = self.state[user_id]
        current_category = self.categories[session["current_category_index"]]
        print(f"➡️ Asking about category index: {session['current_category_index']} — {current_category}")

        example_text = self.food_examples.get(current_category, "")

        if session["current_category_index"] == 0:
            # First message: Full context and polite intro
            system_prompt = """
You are a friendly and professional diet assessment assistant for Wellchemy.

For the first question:
- Welcome the user warmly.
- Explain that this is a quick diet assessment that takes 3-5 minutes.
- Explain that they can answer with terms like "daily", "never", "occasionally", or a number 0-7.
- Make it clear there's no right or wrong answer.
- Be supportive and non-judgmental.
""".strip()

            user_prompt = f"""
Hi there! Could you tell me about how many times in a week you usually enjoy **{current_category}** {example_text}? 
Remember, there's no pressure — answers like "most days", "occasionally", or a number like 3 are perfectly fine!
""".strip()
        else:
            # Subsequent questions: Short, no reintroductions, no instructions, food examples added
            system_prompt = """
You are a friendly diet assessment assistant for Wellchemy.

For follow-up questions:
- Be polite and professional.
- Do NOT reintroduce yourself.
- Do NOT re-explain how to answer.
- Simply ask how often they consume the food category.
- Be direct, short, and positive.

Examples:
- "How often do you consume [food] per week?"
- "On average, how many times per week do you eat [food]?"
- "Can you tell me how often you have [food] in a typical week?"
""".strip()

            user_prompt = f"""
How often per week do you consume **{current_category}** {example_text}?
""".strip()

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            ai_message = response.choices[0].message.content

            return self._format_response(True, "Next question", {
                "response": ai_message
            }, user_id)

        except Exception as e:
            print(f"Error generating next question: {e}")
            return self._format_response(False, "Error", {"error": str(e)}, user_id)

    def _save_and_finish(self, user_id: str, answers: Dict[str, int]) -> Dict[str, Any]:
        """Save collected diet data and finish session."""
        db = SessionLocal()
        try:
            print(f"Saving diet assessment for user {user_id}")
            results = self._calculate_scores(answers)
            record = DietAssessment(
                user_id=user_id,
                results=json.dumps(results),
                date_taken=datetime.utcnow()
            )
            db.add(record)
            db.commit()
            print("Diet assessment saved successfully")
        except Exception as e:
            print(f"Error saving diet assessment: {str(e)}\n{traceback.format_exc()}")
            db.rollback()
            raise
        finally:
            db.close()

        del self.state[user_id]

        summary = self._build_summary(results)

        return self._format_response(True, "Assessment complete", {
            "response": summary
        })

    def _calculate_scores(self, answers: Dict[str, int]) -> Dict[str, Any]:
        """Calculate sub-scores and total score."""
        wpffs = sum(answers.get(food, 0) for food in self.categories if food in self.food_examples and "Fruits" in food or "Vegetables" in food or "Whole Grains" in food or "Legumes" in food or "Nuts" in food or "Plant-based Dairy Alternatives" in food or "Fermented Foods" in food)
        whbs = sum(answers.get(drink, 0) for drink in self.categories if drink in self.food_examples and "Water" in drink or "Herbal Beverages" in drink or "Green Tea" in drink)
        total_score = sum(answers.values())

        return {
            "categories": answers,
            "WholePlantFoodScore": wpffs,
            "WaterHerbalBeverageScore": whbs,
            "TotalDietQualityScore": total_score
        }

    def _build_summary(self, collected_data: Dict[str, Any]) -> str:
        wpffs = collected_data.get("WholePlantFoodScore", 0)
        whbs = collected_data.get("WaterHerbalBeverageScore", 0)
        total_score = collected_data.get("TotalDietQualityScore", 0)

        max_possible_score = len(self.categories) * 7
        gdqs_equivalent = (total_score / max_possible_score) * 40 if max_possible_score else 0

        if gdqs_equivalent < 15:
            risk_level = "High Risk"
        elif gdqs_equivalent < 23:
            risk_level = "Moderate Risk"
        else:
            risk_level = "Low Risk"

        return (
            f"✅ Thanks for completing the diet assessment!\n"
            f"Here's your estimated diet quality summary:\n\n"
            f"🥗 Whole & Plant Food Frequency Score: {wpffs}\n"
            f"💧 Water & Herbal Beverages Score: {whbs}\n"
            f"📊 Diet Risk Level: **{risk_level}**\n\n"
            f"Keep up the great work! If you'd like tips on improving your diet, just let me know. 🌟"
        )
