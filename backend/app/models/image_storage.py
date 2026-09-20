from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from app.database import Base

class StoredImage(Base):
    __tablename__ = "stored_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    content_type = Column(String, default="image/png", nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
