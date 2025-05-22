from typing import Dict, Any
from .base_agent import BaseAgent

class DietaryAssessmentAgent(BaseAgent):
    """Agent responsible for conducting dietary assessments and providing recommendations."""
    
    def __init__(self):
        """Initialize the Dietary Assessment Agent with GPT-3.5-turbo."""
        super().__init__()
        self.system_prompt = """You are the dietary assessment specialist for Wellchemy.
Your role is to:
1. Conduct comprehensive dietary assessments
2. Analyze eating patterns and habits
3. Identify potential nutritional gaps
4. Provide personalized dietary recommendations
5. Suggest specific foods and meal plans
6. Monitor progress and adjust recommendations

Always base your recommendations on scientific evidence and consider the user's:
- Current health status
- Dietary restrictions
- Cultural preferences
- Lifestyle factors
- Personal goals"""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process dietary assessment input and generate recommendations.
        
        Args:
            input_data: Dictionary containing the user's dietary information and context
            
        Returns:
            Dictionary containing the assessment results and recommendations
        """
        try:
            user_message = input_data.get('message', '')
            dietary_data = input_data.get('dietary_data', {})
            health_context = input_data.get('health_context', {})
            
            if not user_message:
                return self._format_response(
                    success=False,
                    message="No message provided"
                )
            
            # Combine all context into the system prompt
            full_system_prompt = self.system_prompt
            if dietary_data:
                full_system_prompt += f"\n\nDietary Data: {dietary_data}"
            if health_context:
                full_system_prompt += f"\n\nHealth Context: {health_context}"
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            return self._format_response(
                success=True,
                message="Assessment completed successfully",
                data={"response": response.choices[0].message.content}
            )
            
        except Exception as e:
            return self._format_response(
                success=False,
                message=f"Error processing request: {str(e)}"
            ) 