"""

test_ingest.py

--------------

Tests for log ingestion endpoints.

"""
 
from fastapi.testclient import TestClient

from app.main import app
 
client = TestClient(app)
 
 
def test_health_check():

    """API should return ok status"""

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"
 
 
def test_ingest_single_log():

    """Single log ingestion should return 200"""

    payload = {

        "timestamp"  : "2025-06-20 10:30:00",

        "source"     : "BillingSystem",

        "log_message": "Backup completed successfully"

    }

    response = client.post("/logs/ingest", json=payload)

    assert response.status_code == 200
 
    data = response.json()

    assert "predicted_label" in data

    assert "severity"        in data

    assert "classifier_used" in data

    assert "alert_sent"      in data
 
 
def test_ingest_missing_fields():

    """Request missing required fields should return 422"""

    payload = {"source": "BillingSystem"}

    response = client.post("/logs/ingest", json=payload)

    assert response.status_code == 422
 
 
def test_ingest_regex_log():

    """Backup log should be handled by regex processor"""

    payload = {

        "timestamp"  : "2025-06-20 10:30:00",

        "source"     : "ModernHR",

        "log_message": "Backup completed successfully"

    }

    response = client.post("/logs/ingest", json=payload)

    assert response.status_code == 200
 
    data = response.json()

    assert data["classifier_used"] == "regex"

    assert data["severity"]        == "LOW"

    assert data["alert_sent"]      == False
 
 
def test_get_logs_returns_list():

    """GET /logs should return paginated list"""

    response = client.get("/logs")

    assert response.status_code == 200
 
    data = response.json()

    assert "logs"  in data

    assert "total" in data

    assert "page"  in data
 
 
def test_get_logs_after_ingest():

    """After ingesting a log GET /logs should return it"""

    payload = {

        "timestamp"  : "2025-06-20 10:30:00",

        "source"     : "BillingSystem",

        "log_message": "Backup completed successfully"

    }

    client.post("/logs/ingest", json=payload)
 
    response = client.get("/logs")

    data = response.json()

    assert data["total"] >= 1
 
 
def test_get_single_log_not_found():

    """GET /logs/9999 should return 404 if log does not exist"""

    response = client.get("/logs/9999")

    assert response.status_code == 404
 