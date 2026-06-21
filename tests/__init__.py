"""

test_alerts.py

--------------

Tests for severity mapping logic.

"""
 
from app.services.alert_service import get_severity
 
 
def test_critical_error_is_critical():

    assert get_severity("Critical Error") == "CRITICAL"
 
 
def test_security_alert_is_critical():

    assert get_severity("Security Alert") == "CRITICAL"
 
 
def test_error_is_high():

    assert get_severity("Error") == "HIGH"
 
 
def test_workflow_error_is_high():

    assert get_severity("Workflow Error") == "HIGH"
 
 
def test_http_status_is_low():

    assert get_severity("HTTP Status") == "LOW"
 
 
def test_user_action_is_low():

    assert get_severity("User Action") == "LOW"
 
 
def test_system_notification_is_low():

    assert get_severity("System Notification") == "LOW"
 
 
def test_resource_usage_is_medium():

    assert get_severity("Resource Usage") == "MEDIUM"
 
 
def test_deprecation_warning_is_medium():

    assert get_severity("Deprecation Warning") == "MEDIUM"
 
 
def test_unknown_label_defaults_to_medium():

    """Any unknown label should safely default to MEDIUM"""

    assert get_severity("SomeRandomUnknownLabel") == "MEDIUM"
 