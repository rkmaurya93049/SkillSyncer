from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ResumeEvaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    jd_title = Column(String)
    resume_filename = Column(String)
    score = Column(Float)
    verdict = Column(String)
    semantic_similarity = Column(Float)
    must_have_score = Column(Float)
    nice_to_have_score = Column(Float)
    degree_match = Column(String)
    experience_match = Column(Float)
    missing_must_have = Column(JSON)
    missing_nice_to_have = Column(JSON)
    suggestions = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)