"""

ingest.py

---------

Handles incoming log ingestion endpoints.
 
POST /logs/ingest  — single log

POST /logs/batch   — multiple logs at once

"""
 
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
 
from app.models.schemas import (

    LogIngestRequest,

    LogClassifyResponse,

    BatchIngestRequest,

    BatchIngestResponse,

)

from app.models.database import get_db

from app.services.classifier  import classify_log

from app.services.alert_service import get_severity, send_slack_alert

from app.services.db_service   import save_log
 
router = APIRouter(prefix="/logs", tags=["Log Ingestion"])
 
 
def process_single_log(log: LogIngestRequest, db: Session) -> LogClassifyResponse:

    """

    Core logic for processing one log.

    Shared by both single and batch endpoints.

    """

    # step 1: classify

    result = classify_log(

        source      = log.source,

        log_message = log.log_message

    )
 
    # step 2: get severity

    severity = get_severity(result["predicted_label"])
 
    # step 3: send alert if needed

    alert_sent = send_slack_alert(

        source          = log.source,

        log_message     = log.log_message,

        predicted_label = result["predicted_label"],

        severity        = severity,

        classifier_used = result["classifier_used"],

    )
 
    # step 4: save to PostgreSQL

    log_data = {

        "timestamp"      : log.timestamp,

        "source"         : log.source,

        "log_message"    : log.log_message,

        "predicted_label": result["predicted_label"],

        "classifier_used": result["classifier_used"],

        "confidence"     : result.get("confidence"),

        "severity"       : severity,

        "alert_sent"     : alert_sent,

    }

    saved = save_log(db, log_data)
 
    # step 5: return response

    return LogClassifyResponse(

        id              = saved.id,

        timestamp       = saved.timestamp,

        source          = saved.source,

        log_message     = saved.log_message,

        predicted_label = saved.predicted_label,

        classifier_used = saved.classifier_used,

        confidence      = saved.confidence,

        severity        = saved.severity,

        alert_sent      = saved.alert_sent,

        processed_at    = saved.processed_at,

    )
 
 
@router.post("/ingest", response_model=LogClassifyResponse)

def ingest_single_log(

    log: LogIngestRequest,

    db : Session = Depends(get_db)

):

    """

    Ingest and classify a single log.
 
    In production this endpoint is called by:

    - Filebeat / Fluentd (log agents)

    - Other microservices directly

    - simulate_logs.py (for local testing)

    """

    try:

        return process_single_log(log, db)

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.post("/batch", response_model=BatchIngestResponse)

def ingest_batch_logs(

    request: BatchIngestRequest,

    db     : Session = Depends(get_db)

):

    """

    Ingest and classify multiple logs in one request.

    Useful for bulk processing or catch-up after downtime.

    """

    results = []

    for log in request.logs:

        try:

            result = process_single_log(log, db)

            results.append(result)

        except Exception as e:

            # don't fail the whole batch for one bad log

            print(f"Failed to process log from {log.source}: {e}")

            continue
 
    return BatchIngestResponse(

        total_received  = len(request.logs),

        total_processed = len(results),

        results         = results,

    )
 