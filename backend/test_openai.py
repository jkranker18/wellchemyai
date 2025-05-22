# test_openai.py

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Print current working directory
print("\nCurrent working directory:", os.getcwd())

# Print ALL environment variables (not just OpenAI ones)
print("\nALL environment variables:")
print("-" * 50)
for key, value in os.environ.items():
    print(f"{key}: {value[:10]}...")  # Only show first 10 chars for security
print("-" * 50)

# Try to find all .env files in the current directory and parent directories
current_dir = Path('.')
env_files = []
while current_dir != current_dir.parent:
    env_file = current_dir / '.env'
    if env_file.exists():
        env_files.append(env_file)
    current_dir = current_dir.parent

print("\nFound .env files:")
for env_file in env_files:
    print(f"- {env_file.absolute()}")

# Explicitly load .env file
env_path = Path('.') / '.env'
print("\nLoading .env file from:", env_path.absolute())
load_dotenv(dotenv_path=env_path, override=True)  # Added override=True

# Print all environment variables again after loading .env
print("\nEnvironment variables AFTER loading .env:")
print("-" * 50)
for key, value in os.environ.items():
    if 'OPENAI' in key.upper():
        print(f"{key}: {value[:10]}...")  # Only show first 10 chars for security
print("-" * 50)

# Load API key and organization ID from environment variables
api_key = os.getenv("OPENAI_API_KEY")
organization = os.getenv("OPENAI_ORG_ID")

# Debug print (only first 10 chars for security)
print("\nDebug - First 10 characters of environment variables:")
print("-" * 50)
print(f"API Key: {api_key[:10] if api_key else 'None'}")
print(f"Org ID: {organization[:10] if organization else 'None'}")
print("-" * 50)

# Safety check
if not api_key or not organization:
    raise ValueError("Missing OPENAI_API_KEY or OPENAI_ORG_ID in environment variables.")

# Set up the API request
headers = {
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Organization": organization,
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "Hello, are you working?"}
    ]
}

# Make the API request
try:
    print("🔁 Testing OpenAI API...")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success! Response from OpenAI:")
        print(result['choices'][0]['message']['content'])
    else:
        print("❌ OpenAI API call failed:")
        print(f"Status code: {response.status_code}")
        print("Response:", response.text)
except Exception as e:
    print("❌ Error making API request:")
    print(e)
