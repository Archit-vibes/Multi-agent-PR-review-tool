from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, unique=True, index=True)

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    state = Column(String)
    title = Column(String)
    body = Column(Text)
    final_review = Column(Text, nullable=True)
    agent_reviews = Column(JSON, nullable=True)
    
class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    action = Column(String, index=True)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
