"""

db_service.py

-------------

All database operations in one place.

Routers call these functions — they never touch SQLAlchemy directly.

"""
 
from sqlalchemy.orm import Session

from app.models.db_models import ClassifiedLog
 
 
def save_log(db: Session, log_data: dict) -> ClassifiedLog:

    """

    Save a classified log record to PostgreSQL.
 
    Args:

        db       : SQLAlchemy session (injected by FastAPI)

        log_data : dict with all fields to save
 
    Returns:

        The saved ClassifiedLog ORM object (includes auto id + processed_at)

    """

    db_log = ClassifiedLog(

        timestamp       = log_data["timestamp"],

        source          = log_data["source"],

        log_message     = log_data["log_message"],

        predicted_label = log_data["predicted_label"],

        classifier_used = log_data["classifier_used"],

        confidence      = log_data.get("confidence"),

        severity        = log_data["severity"],

        alert_sent      = log_data["alert_sent"],

    )

    db.add(db_log)

    db.commit()

    db.refresh(db_log)  # refresh to get the auto-generated id and processed_at

    return db_log
 
 
def get_logs(

    db    : Session,

    page  : int = 1,

    size  : int = 50,

    source: str = None,

    severity: str = None,

    label : str = None,

) -> tuple[list[ClassifiedLog], int]:

    """

    Fetch classified logs with optional filters and pagination.
 
    Returns:

        tuple of (list of logs, total count)

    """

    query = db.query(ClassifiedLog)
 
    # apply optional filters

    if source:

        query = query.filter(ClassifiedLog.source == source)

    if severity:

        query = query.filter(ClassifiedLog.severity == severity)

    if label:

        query = query.filter(ClassifiedLog.predicted_label == label)
 
    total = query.count()
 
    # apply pagination

    logs = (

        query

        .order_by(ClassifiedLog.processed_at.desc())

        .offset((page - 1) * size)

        .limit(size)

        .all()

    )
 
    return logs, total
 
 
def get_log_by_id(db: Session, log_id: int) -> ClassifiedLog | None:

    """

    Fetch a single log by its ID.

    Returns None if not found.

    """

    return db.query(ClassifiedLog).filter(ClassifiedLog.id == log_id).first()
 