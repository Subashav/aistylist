from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SavedResult(Base):
    __tablename__ = "saved_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    clothing_image = Column(String, nullable=False)
    user_image = Column(String, nullable=True)
    clothing_type = Column(String, nullable=False)
    detected_colour = Column(String, nullable=False)
    colour_shade = Column(String, nullable=False)
    hex_value = Column(String, nullable=False)
    rgb_value = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    recommendations = Column(Text, nullable=False)  # JSON serialized
    outfit_suggestions = Column(Text, nullable=False)  # JSON serialized
    explanations = Column(Text, nullable=False)
    personalized_analysis = Column(Text, nullable=True)  # JSON serialized PersonalizedStyleAnalysis
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_results")
