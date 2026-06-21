"""

db_models.py

------------

SQLAlchemy ORM model — defines the PostgreSQL table structure.
 
Table name: classified_logs
 
SQLAlchemy will automatically create this table when the app starts

(we call Base.metadata.create_all in main.py)

"""
 
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text

from sqlalchemy.sql import func

from app.models.database import Base
 
 
class ClassifiedLog(Base):

    """

    Every log that comes through the API gets saved here

    with its classification result and metadata

    """

    __tablename__ = "classified_logs"
 
    id              = Column(Integer, primary_key=True, index=True)
 
    # original log fields

    timestamp       = Column(String,  nullable=False)

    source          = Column(String,  nullable=False, index=True)

    log_message     = Column(Text,    nullable=False)
 
    # classification result

    predicted_label = Column(String,  nullable=False, index=True)

    classifier_used = Column(String,  nullable=False)   # regex / bert / llm

    confidence      = Column(Float,   nullable=True)    # null for regex and llm
 
    # alert metadata

    severity        = Column(String,  nullable=False, index=True)  # CRITICAL/HIGH/MEDIUM/LOW

    alert_sent      = Column(Boolean, default=False)
 
    # auto timestamps

    processed_at    = Column(DateTime(timezone=True), server_default=func.now())
 