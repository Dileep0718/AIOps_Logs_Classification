"""

alert_service.py

----------------

Two responsibilities:

  1. Map a predicted label to a severity level

  2. Send a Slack alert if severity is CRITICAL or HIGH

"""
 
import requests

from app.config import settings
 
# ── severity mapping ───────────────────────────────────────────────────────────

SEVERITY_MAP = {

    "Critical Error"        : "CRITICAL",

    "Security Alert"        : "CRITICAL",

    "Error"                 : "HIGH",

    "Workflow Error"        : "HIGH",

    "Resource Usage"        : "MEDIUM",

    "Deprecation Warning"   : "MEDIUM",

    "HTTP Status"           : "LOW",

    "System Notification"   : "LOW",

    "User Action"           : "LOW",

    "Unclassified"          : "MEDIUM",   # unknown = treat with caution

}
 
# severity levels that trigger an immediate Slack alert

ALERT_ON_SEVERITY = {"CRITICAL", "HIGH"}
 
 
def get_severity(predicted_label: str) -> str:

    """

    Map a predicted label to a severity level.

    Returns MEDIUM if label is not in the map (safe default).

    """

    return SEVERITY_MAP.get(predicted_label, "MEDIUM")
 
 
def send_slack_alert(

    source       : str,

    log_message  : str,

    predicted_label: str,

    severity     : str,

    classifier_used: str

) -> bool:

    """

    Send a Slack alert via webhook.
 
    Returns:

        True  if alert was sent successfully

        False if it failed or severity does not require alerting

    """

    # only alert on CRITICAL and HIGH

    if severity not in ALERT_ON_SEVERITY:

        return False
 
    # pick emoji based on severity

    emoji = "🚨" if severity == "CRITICAL" else "⚠️"
 
    # build the Slack message

    message = {

        "text": f"{emoji} *AIOps Alert — {severity}*",

        "attachments": [

            {

                "color" : "#FF0000" if severity == "CRITICAL" else "#FFA500",

                "fields": [

                    {"title": "Source",     "value": source,          "short": True},

                    {"title": "Label",      "value": predicted_label, "short": True},

                    {"title": "Classifier", "value": classifier_used, "short": True},

                    {"title": "Severity",   "value": severity,        "short": True},

                    {"title": "Log",        "value": log_message[:300], "short": False},

                ]

            }

        ]

    }
 
    try:

        response = requests.post(

            settings.SLACK_WEBHOOK_URL,

            json=message,

            timeout=5       # don't let a slow Slack call block your API

        )

        return response.status_code == 200
 
    except Exception as e:

        # never let alerting failures crash the main app

        print(f"Slack alert failed: {e}")

        return False
 