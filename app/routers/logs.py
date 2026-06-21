"""

logs.py

-------

Read endpoints for querying classified logs.
 
GET /logs           — list logs with optional filters + pagination

GET /logs/{id}      — single log by ID

GET /health         — health check

"""
 
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from typing import Optional
 
from app.models.schemas  import LogClassifyResponse, LogListResponse, HealthResponse

from app.models.database import get_db

from app.services.db_service import get_logs, get_log_by_id

from app.config import settings
 
router = APIRouter(tags=["Logs"])
 
 
@router.get("/health", response_model=HealthResponse)

def health_check():

    """

    Quick check that the API is alive.

    Load balancers and monitoring tools call this.

    """

    return HealthResponse(

        status      = "ok",

        environment = settings.ENVIRONMENT,

        database    = "connected",

    )
 
 
@router.get("/logs", response_model=LogListResponse)

def list_logs(

    page    : int            = Query(default=1,    ge=1,   description="Page number"),

    size    : int            = Query(default=50,   ge=1,   le=200, description="Results per page"),

    source  : Optional[str] = Query(default=None,  description="Filter by source e.g. BillingSystem"),

    severity: Optional[str] = Query(default=None,  description="Filter by severity e.g. CRITICAL"),

    label   : Optional[str] = Query(default=None,  description="Filter by predicted label"),

    db      : Session        = Depends(get_db)

):

    """

    List classified logs with optional filters and pagination.
 
    Examples:

        GET /logs

        GET /logs?severity=CRITICAL

        GET /logs?source=BillingSystem&page=2

        GET /logs?label=Security Alert

    """

    logs, total = get_logs(

        db       = db,

        page     = page,

        size     = size,

        source   = source,

        severity = severity,

        label    = label,

    )
 
    return LogListResponse(

        total = total,

        page  = page,

        size  = size,

        logs  = [

            LogClassifyResponse(

                id              = log.id,

                timestamp       = log.timestamp,

                source          = log.source,

                log_message     = log.log_message,

                predicted_label = log.predicted_label,

                classifier_used = log.classifier_used,

                confidence      = log.confidence,

                severity        = log.severity,

                alert_sent      = log.alert_sent,

                processed_at    = log.processed_at,

            )

            for log in logs

        ],

    )
 
 
@router.get("/logs/{log_id}", response_model=LogClassifyResponse)

def get_single_log(

    log_id: int,

    db    : Session = Depends(get_db)

):

    """

    Fetch a single classified log by its ID.

    Returns 404 if not found.

    """

    log = get_log_by_id(db, log_id)
 
    if not log:

        raise HTTPException(

            status_code = 404,

            detail      = f"Log with id {log_id} not found"

        )
 
    return LogClassifyResponse(

        id              = log.id,

        timestamp       = log.timestamp,

        source          = log.source,

        log_message     = log.log_message,

        predicted_label = log.predicted_label,

        classifier_used = log.classifier_used,

        confidence      = log.confidence,

        severity        = log.severity,

        alert_sent      = log.alert_sent,

        processed_at    = log.processed_at,

    )
 