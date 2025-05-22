# Wellchemy AI

A platform for delivering "food as medicine" solutions using AI agents.

## Project Structure

```
wellchemyai/
├── frontend/           # Next.js frontend application
├── backend/           # Python FastAPI backend
│   ├── venv/         # Python virtual environment
│   ├── main.py       # FastAPI application
│   ├── database.py   # Database configuration
│   ├── models.py     # Database models
│   └── requirements.txt
└── pdfs/             # PDF resources
```

## Setup Instructions

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Unix/MacOS
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a .env file with the following variables:
   ```
   DATABASE_URL=sqlite:///./wellchemy.db
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

## Development

- Frontend runs on: http://localhost:3000
- Backend API runs on: http://localhost:8000
- API documentation available at: http://localhost:8000/docs 