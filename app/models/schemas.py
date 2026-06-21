"""

schemas.py

----------

Pydantic models that define the shape of:

  - incoming API requests  (what the caller must send)

  - outgoing API responses (what your API returns)
 
FastAPI uses these automatically for:

  - request validation  (wrong field? auto 422 error)

  - response serialization

  - auto Swagger docs at /docs

"""
 
from pydantic import BaseModel, Field

from typing import Optional

from datetime import datetime
 
 
# ── REQUEST models (what comes IN to your API) ────────────────────────────────
 
class LogIngestRequest(BaseModel):

    """

    Shape of a single log sent to POST /logs/ingest

    This is what Filebeat / simulate_logs.py sends to your API

    """

    timestamp : str             = Field(..., example="2025-06-20 10:30:00")

    source    : str             = Field(..., example="BillingSystem")

    log_message: str            = Field(..., example="Payment failed for order 8291")
 
    class Config:

        # allows extra fields to be ignored instead of causing errors

        extra = "ignore"
 
 
class BatchIngestRequest(BaseModel):

    """

    Shape of a batch of logs sent to POST /logs/batch

    Sends multiple logs in one request

    """

    logs: list[LogIngestRequest]
 
 
# ── RESPONSE models (what goes OUT from your API) ─────────────────────────────
 
class LogClassifyResponse(BaseModel):

    """

    What your API returns after classifying a single log

    """

    id              : Optional[int] = None

    timestamp       : str

    source          : str

    log_message     : str

    predicted_label : str

    classifier_used : str           # "regex", "bert", or "llm"

    confidence      : Optional[float] = None   # only bert gives confidence score

    severity        : str           # "CRITICAL", "HIGH", "MEDIUM", "LOW"

    alert_sent      : bool          # was a Slack alert fired?

    processed_at    : Optional[datetime] = None
 
 
class BatchIngestResponse(BaseModel):

    """

    What your API returns after processing a batch of logs

    """

    total_received  : int

    total_processed : int

    results         : list[LogClassifyResponse]
 
 
class HealthResponse(BaseModel):

    """

    What GET /health returns

    """

    status          : str  = "ok"

    environment     : str

    database        : str  = "connected"
 
 
class LogListResponse(BaseModel):

    """

    What GET /logs returns — paginated list of classified logs

    """

    total  : int

    page   : int

    size   : int

    logs   : list[LogClassifyResponse]
 