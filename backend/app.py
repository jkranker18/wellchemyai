from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from agents import PrimaryAssistant, UserAgent, DietaryAssessmentAgent

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],  # Frontend URL
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize agents
primary_assistant = PrimaryAssistant()
user_agent = UserAgent()
dietary_agent = DietaryAssessmentAgent()

@app.route('/chat', methods=['POST'])
def chat():
    """Handle general chat messages using the primary assistant."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        response = primary_assistant.process(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user', methods=['POST'])
def user():
    """Handle user-related queries using the user agent."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        response = user_agent.process(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dietary', methods=['POST'])
def dietary():
    """Handle dietary assessment queries using the dietary agent."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        response = dietary_agent.process(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)