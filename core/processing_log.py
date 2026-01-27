from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from core.database import Base

class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    processing_time = Column(Float)
    status = Column(String)
    processed_img = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
