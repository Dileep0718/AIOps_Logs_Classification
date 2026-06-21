"""

test_classifier.py

------------------

Tests for hybrid classifier routing logic.

"""
 
from unittest.mock import patch

from app.services.classifier import classify_log
 
 
def test_regex_catches_backup_log():

    """Backup log should be caught by regex"""

    result = classify_log("ModernHR", "Backup completed successfully")

    assert result["classifier_used"] == "regex"

    assert result["predicted_label"] == "System Notification"

    assert result["confidence"]      is None
 
 
def test_regex_catches_http_log():

    """HTTP log should be caught by regex"""

    result = classify_log("BillingSystem", "HTTP GET /api/users status 200")

    assert result["classifier_used"] == "regex"

    assert result["predicted_label"] == "HTTP Status"
 
 
def test_legacycrm_always_uses_llm():

    """LegacyCRM logs must always route to LLM"""

    with patch("app.services.classifier.classify_with_llm") as mock_llm:

        mock_llm.return_value = "Workflow Error"

        result = classify_log("LegacyCRM", "Some legacy system log")

        assert result["classifier_used"] == "llm"

        mock_llm.assert_called_once()
 
 
def test_result_always_has_required_keys():

    """Every classification result must have these three keys"""

    result = classify_log("BillingSystem", "Backup completed successfully")

    assert "predicted_label" in result

    assert "classifier_used" in result

    assert "confidence"      in result
 
 
def test_bert_fallback_when_regex_fails():

    """When regex returns None BERT should be used"""

    with patch("app.services.classifier.classify_with_regex") as mock_regex, patch("app.services.classifier.classify_with_bert")  as mock_bert:
        mock_regex.return_value = None

        mock_bert.return_value  = ("Error", 0.91)

        result = classify_log("BillingSystem", "Some complex log message")

        assert result["classifier_used"] == "bert"

        assert result["predicted_label"] == "Error"

        assert result["confidence"]      == 0.91
 