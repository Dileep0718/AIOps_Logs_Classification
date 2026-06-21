"""

train_model.py

--------------

Run this ONCE to train the log classifier and save the model.
 
Usage:

    python training/train_model.py
 
Output:

    ml_models/log_classifier.joblib

"""
 
import os

import sys

import joblib

import pandas as pd

from sentence_transformers import SentenceTransformer

from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score, classification_report
 
# ── paths ─────────────────────────────────────────────────────────────────────

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH   = os.path.join(ROOT_DIR, "training", "synthetic_logs.csv")

OUTPUT_DIR  = os.path.join(ROOT_DIR, "ml_models")

OUTPUT_PATH = os.path.join(OUTPUT_DIR, "log_classifier.joblib")
 
# ── sanity check ──────────────────────────────────────────────────────────────

if not os.path.exists(DATA_PATH):

    print(f"ERROR: Dataset not found at {DATA_PATH}")

    print("Make sure synthetic_logs.csv is inside the training/ folder.")

    sys.exit(1)
 
os.makedirs(OUTPUT_DIR, exist_ok=True)
 
# ── step 1: load data ─────────────────────────────────────────────────────────

print("=" * 60)

print("STEP 1: Loading dataset...")

print("=" * 60)
 
df = pd.read_csv(DATA_PATH)

print(f"Total rows loaded : {len(df)}")

print(f"\nLabel distribution:")

print(df["target_label"].value_counts().to_string())
 
# ── step 2: filter out LegacyCRM ─────────────────────────────────────────────

print("\n" + "=" * 60)

print("STEP 2: Filtering out LegacyCRM logs (handled by LLM)...")

print("=" * 60)
 
df_train = df[df["source"] != "LegacyCRM"].copy()

print(f"Rows after filtering : {len(df_train)}  (removed {len(df) - len(df_train)} LegacyCRM rows)")
 
# ── step 3: prepare features and labels ──────────────────────────────────────

print("\n" + "=" * 60)

print("STEP 3: Preparing features and labels...")

print("=" * 60)
 
X_text = df_train["log_message"].astype(str).tolist()

y      = df_train["target_label"].astype(str).tolist()
 
print(f"Total training samples : {len(X_text)}")

print(f"Unique labels          : {sorted(set(y))}")
 
# ── step 4: encode with sentence transformer ──────────────────────────────────

print("\n" + "=" * 60)

print("STEP 4: Encoding log messages with sentence-transformers...")

print("        Model: all-MiniLM-L6-v2  (downloads on first run ~80MB)")

print("=" * 60)
 
encoder = SentenceTransformer("all-MiniLM-L6-v2")

X_embeddings = encoder.encode(

    X_text,

    show_progress_bar=True,

    batch_size=64

)

print(f"Embedding shape: {X_embeddings.shape}")
 
# ── step 5: train / test split ────────────────────────────────────────────────

print("\n" + "=" * 60)

print("STEP 5: Splitting into train / test sets (80/20)...")

print("=" * 60)
 
X_train, X_test, y_train, y_test = train_test_split(

    X_embeddings,

    y,

    test_size=0.2,

    random_state=42,

    stratify=y

)

print(f"Train samples : {len(X_train)}")

print(f"Test samples  : {len(X_test)}")
 
# ── step 6: train logistic regression ─────────────────────────────────────────

print("\n" + "=" * 60)

print("STEP 6: Training Logistic Regression classifier...")

print("=" * 60)
model = LogisticRegression(
    max_iter=1000,
    random_state=42,
    C=1.0
)
model.fit(X_train, y_train)
print("Training complete.")
 
# ── step 7: evaluate ──────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 7: Evaluating on test set...")
print("=" * 60)
y_pred   = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ── step 8: save the model ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 8: Saving model...")
print("=" * 60)
joblib.dump(
    {
        "model"  : model,
        "encoder": encoder
    },
    OUTPUT_PATH
)

print(f"\nModel saved at : {OUTPUT_PATH}")
print("\n" + "=" * 60)
print("ALL DONE! Next step: run the FastAPI app")
print("    uvicorn app.main:app --reload")
print("=" * 60)
 