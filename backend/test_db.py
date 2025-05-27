from db_connection import SessionLocal
from models import User, DietAssessment, ChatMessage
from datetime import datetime
import bcrypt

def test_database():
    """Test database setup and create some test data."""
    db = SessionLocal()
    try:
        # Create a test user
        test_user = User(
            email="test@example.com",
            password_hash=bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()),
            first_login=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Created test user with ID: {test_user.user_id}")

        # Create a test assessment
        test_assessment = DietAssessment(
            user_id=test_user.user_id,
            question_scores={"q1": 5, "q2": 3, "q3": 4},
            total_score=12.0,
            max_score=15.0,
            percent=80.0
        )
        db.add(test_assessment)
        db.commit()
        print(f"Created test assessment with ID: {test_assessment.assessment_id}")

        # Create a test chat message
        test_message = ChatMessage(
            user_id=test_user.user_id,
            message="Hello, this is a test message",
            response="Hi! This is a test response",
            agent_type="primary"
        )
        db.add(test_message)
        db.commit()
        print(f"Created test chat message with ID: {test_message.id}")

        # Verify data was created
        user = db.query(User).first()
        print(f"\nVerifying data:")
        print(f"User found: {user.email}")
        print(f"User has {len(user.assessments)} assessments")
        print(f"User has {len(user.chat_messages)} chat messages")

    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database() 