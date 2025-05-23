from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agents import PrimaryAssistant

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

primary_assistant = PrimaryAssistant()

@app.route('/chat', methods=['POST'])
def chat():
    """Unified chat entry point for all agents via PrimaryAssistant."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        response = primary_assistant.process(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
