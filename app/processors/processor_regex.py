"""

processor_regex.py

------------------

Fast pattern matching using regex.

Handles simple, predictable log patterns.

Returns None if no pattern matches — classifier.py then falls back to BERT.

"""
 
import re
 
# patterns mapped to labels

# order matters — first match wins

PATTERNS = [

    (r"HTTP.*?(\d{3})",                          "HTTP Status"),

    (r"User .* (logged in|logged out|login)",    "User Action"),

    (r"Account.*created",                        "User Action"),

    (r"uploaded successfully",                   "System Notification"),

    (r"Backup completed",                        "System Notification"),

    (r"(replication|backup).*(failed|error)",    "Error"),

    (r"memory|cpu|disk",                         "Resource Usage"),

    (r"deprecated|deprecation",                  "Deprecation Warning"),

]
 
 
def classify_with_regex(log_message: str) -> str | None:

    """

    Try to match the log message against known patterns.
 
    Returns:

        label (str)  if a pattern matches

        None         if no pattern matches — signals fallback to BERT

    """

    message_lower = log_message.lower()
 
    for pattern, label in PATTERNS:

        if re.search(pattern, message_lower, re.IGNORECASE):

            return label
 
    return None
 