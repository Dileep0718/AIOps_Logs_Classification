"""

simulate_logs.py

----------------

Simulates a real log agent (like Filebeat) sending logs to your API.
 
Reads synthetic_logs.csv row by row and POSTs each log

to POST /logs/ingest with a small delay between them.
 
Usage:

    # make sure your API is running first:

    uvicorn app.main:app --reload
 
    # then in a second terminal:

    python simulate_logs.py
 
Watch your terminal and Slack channel —

CRITICAL and HIGH logs will trigger alerts in real time.

"""
 
import time

import requests

import pandas as pd
 
# ── config ────────────────────────────────────────────────────────────────────

API_URL    = "http://localhost:8000/logs/ingest"

DATA_PATH  = "training/synthetic_logs.csv"

DELAY      = 0.5    # seconds between each log — adjust as needed
 
# ── load dataset ──────────────────────────────────────────────────────────────

print("=" * 60)

print("AIOps Log Simulator — Fake Log Agent")

print("=" * 60)

print(f"Reading logs from : {DATA_PATH}")

print(f"Sending to        : {API_URL}")

print(f"Delay per log     : {DELAY}s")

print("=" * 60)

print()
 
df = pd.read_csv(DATA_PATH)

total = len(df)

print(f"Total logs to send: {total}")

print("Starting in 3 seconds... (Ctrl+C to stop)")

time.sleep(3)
 
# ── send logs one by one ──────────────────────────────────────────────────────

success_count = 0

fail_count    = 0
 
for index, row in df.iterrows():

    payload = {

        "timestamp"  : str(row["timestamp"]),

        "source"     : str(row["source"]),

        "log_message": str(row["log_message"]),

    }
 
    try:

        response = requests.post(API_URL, json=payload, timeout=10)
 
        if response.status_code == 200:

            data = response.json()

            success_count += 1

            # print summary for each log

            alert_icon = "🚨" if data["alert_sent"] else "  "

            print(

                f"{alert_icon} [{index+1}/{total}] "

                f"{data['source']:<20} "

                f"{data['predicted_label']:<22} "

                f"{data['severity']:<8} "

                f"via {data['classifier_used']}"

            )

        else:

            fail_count += 1

            print(f"  [{index+1}/{total}] FAILED — status {response.status_code}")
 
    except requests.exceptions.ConnectionError:

        print("\nERROR: Cannot connect to API.")

        print("Make sure the API is running: uvicorn app.main:app --reload")

        break
 
    except Exception as e:

        fail_count += 1

        print(f"  [{index+1}/{total}] ERROR — {e}")
 
    time.sleep(DELAY)
 
# ── summary ───────────────────────────────────────────────────────────────────

print()

print("=" * 60)

print(f"Simulation complete!")

print(f"  Sent successfully : {success_count}")

print(f"  Failed            : {fail_count}")

print("=" * 60)
 