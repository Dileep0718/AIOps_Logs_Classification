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
 
from pydantic import BaseModel, ConfigDict

from typing import Optional

from datetime import datetime
 
 
class LogIngestRequest(BaseModel):

    model_config = ConfigDict(extra="ignore")
 
    timestamp  : str

    source     : str

    log_message: str
 
 
class BatchIngestRequest(BaseModel):

    logs: list[LogIngestRequest]
 
 
class LogClassifyResponse(BaseModel):

    id              : Optional[int]      = None

    timestamp       : str

    source          : str

    log_message     : str

    predicted_label : str

    classifier_used : str

    confidence      : Optional[float]    = None

    severity        : str

    alert_sent      : bool

    processed_at    : Optional[datetime] = None
 
 
class BatchIngestResponse(BaseModel):

    total_received  : int

    total_processed : int

    results         : list[LogClassifyResponse]
 
 
class HealthResponse(BaseModel):

    status     : str = "ok"

    environment: str

    database   : str = "connected"
 
 
class LogListResponse(BaseModel):

    total: int

    page : int

    size : int

    logs : list[LogClassifyResponse]
 