"""

processor_bert.py

-----------------

Classifies logs using sentence-transformers + Logistic Regression.
 
Loads the trained model from ml_models/log_classifier.joblib

which contains both:

  - encoder : SentenceTransformer (all-MiniLM-L6-v2)

  - model   : LogisticRegression
 
Returns "Unclassified" if max confidence is below threshold.

"""
 
import os

import joblib

import numpy as np
 
# ── load model once at module level ───────────────────────────────────────────

# loading is expensive — we do it once when the app starts,

# not on every request

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH  = os.path.join(ROOT_DIR, "ml_models", "log_classifier.joblib")
 
print(f"Loading BERT classifier from: {MODEL_PATH}")

_artifacts  = joblib.load(MODEL_PATH)

_encoder    = _artifacts["encoder"]

_model      = _artifacts["model"]

print("BERT classifier loaded successfully.")
 
# confidence threshold — below this we return Unclassified

CONFIDENCE_THRESHOLD = 0.5
 
 
def classify_with_bert(log_message: str) -> tuple[str, float]:

    """

    Classify a log message using sentence embeddings + logistic regression.
 
    Returns:

        tuple of (label, confidence)

        label is "Unclassified" if confidence is below threshold

    """

    # encode the message into a vector

    embedding = _encoder.encode([log_message])
 
    # get prediction probabilities for all labels

    probabilities = _model.predict_proba(embedding)[0]

    max_confidence = float(np.max(probabilities))
 
    if max_confidence < CONFIDENCE_THRESHOLD:

        return "Unclassified", max_confidence
 
    # get the label with highest probability

    predicted_index = np.argmax(probabilities)

    predicted_label = _model.classes_[predicted_index]
 
    return predicted_label, max_confidence
 