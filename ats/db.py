# ats/db.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class ResumeRecord(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
    parsed_json = Column(Text, nullable=False)
    jd_text = Column(Text, nullable=False)
    score_json = Column(Text, nullable=False)
    gemini_explain = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(path="sqlite:///ats_results.db"):
    engine = create_engine(path, echo=False, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)
