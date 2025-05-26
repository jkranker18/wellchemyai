from typing import Dict, Any
from .base_agent import BaseAgent
from sqlalchemy.orm import Session
from db_connection import SessionLocal
from models import User
from datetime import datetime

class UserAgent(BaseAgent):
    """Agent responsible for handling new user onboarding and login processes."""

    def __init__(self):
        super().__init__()
        self.system_message = """You are the user management assistant for Wellchemy."""

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            email = data.get("email", "guest@wellchemy.ai")
            user = db.query(User).filter_by(email=email).first()

            if not user:
                user = User(
                    email=email,
                    password_hash="auto-created",
                    first_login=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                new = True
            else:
                user.last_login = datetime.utcnow()
                db.commit()
                new = False

            return self._format_response(True, "User onboarded", {
                "response": f"Welcome{' back' if not new else ''}, {user.email}!",
                "user_id": user.user_id,
                "agent_type": "user"
            })
        finally:
            db.close()

    def _format_response(self, success: bool, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        return {
            "success": success,
            "message": message,
            "data": data or {}
        }
