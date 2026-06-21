from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ScanRecord(Base):
    __tablename__ = "scan_records"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_issues = Column(Integer, nullable=False)
    issues = Column(JSONB, nullable=False)  # Full issue list stored as JSONB
