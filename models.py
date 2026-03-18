from sqlalchemy import Column, Integer, Text, String, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class RagHistory(Base):
    __tablename__ = "rag_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    sources = Column(Text)
    document_name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())