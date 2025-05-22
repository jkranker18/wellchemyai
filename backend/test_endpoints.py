import requests
import json
import asyncio
from app import app

def test_health():
    """Test the health check endpoint."""
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {'status': 'healthy'}
        print("✅ Health check endpoint working")

def test_chat():
    """Test the chat endpoint with the primary assistant."""
    with app.test_client() as client:
        data = {
            "message": "What is food as medicine?"
        }
        response = client.post('/chat', json=data)
        if response.status_code != 200:
            print(f"❌ Chat endpoint failed with status code {response.status_code}")
            print("Response content:", response.data.decode())
        assert response.status_code == 200
        result = response.json
        assert 'success' in result
        assert 'message' in result
        assert 'data' in result
        assert 'response' in result['data']
        print("✅ Chat endpoint working")
        print("Response:", result['data']['response'])

def test_user():
    """Test the user endpoint with the user agent."""
    with app.test_client() as client:
        data = {
            "message": "I'm a new user, how do I get started?",
            "context": {"is_new_user": True}
        }
        response = client.post('/user', json=data)
        assert response.status_code == 200
        result = response.json
        assert 'success' in result
        assert 'message' in result
        assert 'data' in result
        assert 'response' in result['data']
        print("✅ User endpoint working")
        print("Response:", result['data']['response'])

def test_dietary():
    """Test the dietary endpoint with the dietary assessment agent."""
    with app.test_client() as client:
        data = {
            "message": "I want to improve my diet",
            "dietary_data": {
                "current_diet": "Standard American Diet",
                "restrictions": ["No nuts", "Lactose intolerant"]
            },
            "health_context": {
                "goals": ["Improve energy", "Better digestion"],
                "conditions": ["IBS"]
            }
        }
        response = client.post('/dietary', json=data)
        assert response.status_code == 200
        result = response.json
        assert 'success' in result
        assert 'message' in result
        assert 'data' in result
        assert 'response' in result['data']
        print("✅ Dietary endpoint working")
        print("Response:", result['data']['response'])

if __name__ == '__main__':
    print("Testing Wellchemy AI Backend Endpoints...")
    print("\n1. Testing Health Check...")
    test_health()
    
    print("\n2. Testing Chat Endpoint...")
    test_chat()
    
    print("\n3. Testing User Endpoint...")
    test_user()
    
    print("\n4. Testing Dietary Endpoint...")
    test_dietary()
    
    print("\nAll tests completed! 🎉") 