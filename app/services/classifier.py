"""

classifier.py

-------------

Hybrid classification logic.
 
Routing rules:

  1. LegacyCRM source     → always use LLM (no training data for this source)

  2. All other sources    → try Regex first

                          → if Regex returns None, use BERT

                          → if BERT returns Unclassified, use LLM
 
This gives us:

  - Speed    : regex handles simple patterns instantly

  - Accuracy : BERT handles complex patterns well

  - Coverage : LLM handles anything that falls through

"""
 
from app.processors.processor_regex import classify_with_regex

from app.processors.processor_bert  import classify_with_bert

from app.processors.processor_llm   import classify_with_llm
 
 
def classify_log(source: str, log_message: str) -> dict:

    """

    Classify a single log message using the hybrid approach.
 
    Args:

        source      : where the log came from (e.g. "BillingSystem")

        log_message : the actual log text
 
    Returns:

        dict with keys:

            predicted_label : str

            classifier_used : str   ("regex", "bert", "llm")

            confidence      : float or None

    """
 
    # ── route 1: LegacyCRM always goes to LLM ─────────────────────────────

    if source == "LegacyCRM":

        label = classify_with_llm(log_message)

        return {

            "predicted_label": label,

            "classifier_used": "llm",

            "confidence"     : None

        }
 
    # ── route 2: try regex first ───────────────────────────────────────────

    label = classify_with_regex(log_message)

    if label is not None:

        return {

            "predicted_label": label,

            "classifier_used": "regex",

            "confidence"     : None

        }
 
    # ── route 3: regex failed — try BERT ──────────────────────────────────

    label, confidence = classify_with_bert(log_message)

    if label != "Unclassified":

        return {

            "predicted_label": label,

            "classifier_used": "bert",

            "confidence"     : round(confidence, 4)

        }
 
    # ── route 4: BERT not confident enough — fall back to LLM ─────────────

    label = classify_with_llm(log_message)

    return {

        "predicted_label": label,

        "classifier_used": "llm",

        "confidence"     : None

    }
 