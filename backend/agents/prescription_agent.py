import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_agent import BaseAgent

class PrescriptionAgent(BaseAgent):
    def __init__(self, programs: Dict[str, Any], chronic_condition_diet_mapping: Dict[str, Any]):
        super().__init__()
        self.programs = programs
        self.chronic_condition_diet_mapping = chronic_condition_diet_mapping
        
        # Load inventory data from the data directory
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        with open(os.path.join(data_dir, "inventory.json")) as f:
            self.inventory = json.load(f)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process prescription-related requests."""
        try:
            user_id = input_data.get("user_id")
            diet_assessment = input_data.get("diet_assessment", {})
            eligibility_assessment = input_data.get("eligibility_assessment", {})
            
            orders = self.generate_prescription(user_id, diet_assessment, eligibility_assessment)
            
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
            })
            
        except Exception as e:
            return self._format_response(False, "Error generating prescription", {
                "error": str(e)
            })

    def generate_prescription(self, user_id, diet_assessment, eligibility_assessment):
        program = self.match_program(eligibility_assessment)

        if not program:
            raise Exception("No matching program found.")

        meals = self.filter_inventory(program, diet_assessment, eligibility_assessment)

        if not meals:
            raise Exception("No meals found matching the user's dietary needs and preferences.")

        orders = self.generate_orders(user_id, program, meals)
        return orders

    def match_program(self, eligibility_assessment):
        payer = eligibility_assessment.get("insurance_provider", "").lower()
        for program in self.programs:
            if "payer" in program and payer in program["payer"].lower():
                return program
        print(f"❌ No program found for payer: {payer}")
        return None

    def filter_inventory(self, program, diet_assessment, eligibility_assessment):
        available_meals = [meal for meal in self.inventory if meal["food_type"] == program["food_type"] and meal["stock"] > 0]

        available_meals = self.filter_restrictions(available_meals, eligibility_assessment.get("dietary_restrictions", []))

        recommended_tags = set()
        for condition in eligibility_assessment.get("chronic_conditions", []):
            recommended_tags.update(self.chronic_condition_diet_mapping.get(condition, []))

        available_meals = self.filter_diet_tags(available_meals, recommended_tags)

        available_meals = self.filter_preferences(available_meals, diet_assessment)

        available_meals.sort(key=lambda meal: -meal["stock"])

        return available_meals

    def filter_restrictions(self, meals, restrictions):
        filtered = []
        for meal in meals:
            if not any(restricted.lower() in ingredient.lower() for restricted in restrictions for ingredient in meal["ingredients"]):
                filtered.append(meal)
        return filtered

    def filter_diet_tags(self, meals, recommended_tags):
        if not recommended_tags:
            return meals
        filtered = []
        for meal in meals:
            if any(tag in meal["diet_tags"] for tag in recommended_tags):
                filtered.append(meal)
        return filtered

    def filter_preferences(self, meals, preferences):
        if preferences.get("vegetarian"):
            restricted_meats = ["chicken", "beef", "pork", "fish", "turkey", "lamb"]
            return [meal for meal in meals if not any(meat in ingredient.lower() for meat in restricted_meats for ingredient in meal["ingredients"])]
        return meals

    def generate_orders(self, user_id, program, meals):
        quantity = program["quantity_per_delivery"]
        frequency_days = program["frequency_days"]
        total_weeks = program["duration_weeks"]

        orders = []
        delivery_date = datetime.now()

        meal_ids = [meal["id"] for meal in meals]

        for week in range(total_weeks):
            selected_meals = self.select_meals(meal_ids, quantity)
            order = {
                "order_id": str(uuid.uuid4()),
                "user_id": user_id,
                "program_id": program["id"],
                "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                "meals": selected_meals
            }
            orders.append(order)
            delivery_date += timedelta(days=frequency_days)

        return orders

    def select_meals(self, meal_ids, quantity):
        selected = []
        idx = 0
        while len(selected) < quantity:
            meal = meal_ids[idx % len(meal_ids)]
            selected.append(meal)
            idx += 1
        return selected
