from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    """Model for storing user information."""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_login = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    diet_assessments = relationship("DietAssessment", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    eligibility_assessments = relationship("EligibilityAssessment", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'first_login': self.first_login.isoformat() if self.first_login else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class DietAssessment(Base):
    """Model for storing diet assessment results."""
    __tablename__ = 'diet_assessments'
    
    assessment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    results = Column(Text, nullable=False)  # Store JSON as Text in SQLite
    date_taken = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diet_assessments")

    def to_dict(self):
        return {
            "assessment_id": self.assessment_id,
            "user_id": self.user_id,
            "results": self.results,  # This will be a JSON string
            "date_taken": self.date_taken.isoformat()
        }

class ChatMessage(Base):
    """Model for storing chat messages."""
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    message = Column(String, nullable=False)
    response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_type = Column(String(50), nullable=False)  # e.g., 'primary', 'dietary', 'user'

    user = relationship("User", back_populates="chat_messages")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.isoformat(),
            'agent_type': self.agent_type
        }

class EligibilityAssessment(Base):
    __tablename__ = 'eligibility_assessments'

    assessment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    answers = Column(Text, nullable=False)  # Store JSON as Text in SQLite
    date_taken = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="eligibility_assessments") 