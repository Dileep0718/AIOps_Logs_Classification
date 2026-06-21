# 🤖 AIOps Log Classification System

> An enterprise-grade, real-time log classification pipeline using a **hybrid NLP approach** — combining Regex, Sentence-BERT, and LLM to automatically classify application logs, assess severity, and trigger Slack alerts.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![CI](https://github.com/YOUR_USERNAME/aiops-log-classification/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📌 What is this?

In any large-scale software system, hundreds of microservices generate thousands of log lines every minute. Manually monitoring these logs is impossible. This project solves that problem by:

- **Automatically ingesting** logs via a REST API (simulating what Filebeat/Fluentd does in production)
- **Classifying** each log into one of 9 categories using a 3-tier hybrid NLP model
- **Assessing severity** and routing CRITICAL/HIGH logs to Slack alerts in real time
- **Persisting** all classified logs to PostgreSQL for querying and auditing

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────┐
                        │        Log Sources               │
                        │  App Servers · Docker · K8s      │
                        └──────────────┬──────────────────┘
                                       │  writes logs
                                       ▼
                        ┌─────────────────────────────────┐
                        │     Log Agent (Filebeat)         │
                        │  watches log files, forwards     │
                        │  (simulated by simulate_logs.py) │
                        └──────────────┬──────────────────┘
                                       │  POST /logs/ingest
                                       ▼
                        ┌─────────────────────────────────┐
                        │     FastAPI Ingestion Layer      │
                        │  POST /logs/ingest               │
                        │  POST /logs/batch                │
                        └──────────────┬──────────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────────┐
                        │      Hybrid Classifier           │
                        │                                  │
                        │  Step 1: Regex                   │
                        │    ↓ (if no match)               │
                        │  Step 2: BERT + Logistic Reg     │
                        │    ↓ (if confidence < 0.5)       │
                        │  Step 3: LLM (Groq/DeepSeek)    │
                        │                                  │
                        │  LegacyCRM → always uses LLM    │
                        └──────────────┬──────────────────┘
                                       │
                          ┌────────────┴────────────┐
                          ▼                         ▼
            ┌─────────────────────┐   ┌─────────────────────────┐
            │   Severity Router   │   │    PostgreSQL            │
            │                     │   │                          │
            │ CRITICAL → 🚨 Slack │   │  All classified logs     │
            │ HIGH     → ⚠️ Slack  │   │  persisted with full     │
            │ MEDIUM   → store    │   │  metadata                │
            │ LOW      → store    │   └─────────────────────────┘
            └─────────────────────┘
```

---

## 🧠 Hybrid Classification Logic

The system uses a 3-tier fallback strategy — optimizing for **speed, accuracy, and coverage**:

| Tier | Model | Used When | Speed |
|------|-------|-----------|-------|
| 1 | **Regex** | Simple predictable patterns (HTTP status, backup logs) | ~1ms |
| 2 | **Sentence-BERT + Logistic Regression** | Complex log messages, confidence > 0.5 | ~50ms |
| 3 | **LLM (Groq / DeepSeek)** | LegacyCRM logs, BERT confidence < 0.5 | ~800ms |

### Why this order?

- **Regex first** — handles 500/2410 logs instantly with zero ML overhead
- **BERT second** — handles 1903/2410 logs accurately using `all-MiniLM-L6-v2` embeddings
- **LLM last** — handles only 7 LegacyCRM logs + edge cases that fall through

> This design mirrors real AIOps systems where cost and latency are optimized by reserving expensive LLM calls for only the cases that truly need them.

---

## 📊 Log Labels & Severity Mapping

| Label | Severity | Alert |
|-------|----------|-------|
| Critical Error | 🔴 CRITICAL | Slack immediately |
| Security Alert | 🔴 CRITICAL | Slack immediately |
| Error | 🟠 HIGH | Slack immediately |
| Workflow Error | 🟠 HIGH | Slack immediately |
| Resource Usage | 🟡 MEDIUM | Stored only |
| Deprecation Warning | 🟡 MEDIUM | Stored only |
| HTTP Status | 🟢 LOW | Stored only |
| System Notification | 🟢 LOW | Stored only |
| User Action | 🟢 LOW | Stored only |

---

## 🗂️ Project Structure

```
aiops-log-classification/
│
├── app/
│   ├── main.py                    # FastAPI app, startup, router registration
│   ├── config.py                  # Pydantic Settings — env vars, secrets
│   ├── routers/
│   │   ├── ingest.py              # POST /logs/ingest, POST /logs/batch
│   │   └── logs.py                # GET /logs, GET /logs/{id}, GET /health
│   ├── services/
│   │   ├── classifier.py          # hybrid routing logic
│   │   ├── alert_service.py       # severity mapping + Slack webhook
│   │   └── db_service.py          # PostgreSQL read/write
│   ├── processors/
│   │   ├── processor_regex.py     # regex pattern matching
│   │   ├── processor_bert.py      # sentence-transformers + logistic regression
│   │   └── processor_llm.py       # Groq LLM (DeepSeek) fallback
│   └── models/
│       ├── schemas.py             # Pydantic request/response models
│       ├── db_models.py           # SQLAlchemy ORM table definition
│       └── database.py            # engine, session, Base
│
├── training/
│   ├── synthetic_logs.csv         # 2,410 labelled log samples
│   └── train_model.py             # trains and saves log_classifier.joblib
│
├── ml_models/
│   └── log_classifier.joblib      # trained model (auto-generated, git-ignored)
│
├── tests/
│   ├── conftest.py                # test DB setup, ML model mocks
│   ├── test_ingest.py             # API endpoint tests
│   ├── test_classifier.py         # classifier routing tests
│   └── test_alerts.py             # severity mapping tests
│
├── docker/
│   ├── Dockerfile                 # containerize the app
│   └── docker-compose.yml         # app + postgres together
│
├── .github/workflows/
│   └── ci.yml                     # lint → test → docker build
│
├── simulate_logs.py               # fake log agent — streams CSV to API
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL running locally
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Slack webhook URL (free — [setup guide](https://api.slack.com/messaging/webhooks))

### 1. Clone and set up

```bash
git clone https://github.com/YOUR_USERNAME/aiops-log-classification.git
cd aiops-log-classification

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# edit .env and fill in your values
```

```bash
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/aiops_logs
GROQ_API_KEY=your_groq_api_key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
ENVIRONMENT=development
```

### 3. Create the database

```bash
psql -U postgres -c "CREATE DATABASE aiops_logs;"
```

### 4. Train the model

```bash
python training/train_model.py
```

This trains the BERT + Logistic Regression classifier on `synthetic_logs.csv` and saves it to `ml_models/log_classifier.joblib`.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

API is live at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### 6. Simulate real-time log ingestion

In a second terminal:

```bash
python simulate_logs.py
```

This streams all 2,410 logs to your API one by one — mimicking what Filebeat does in production. Watch your Slack channel for CRITICAL and HIGH alerts firing in real time.

---

## 🐳 Run with Docker

```bash
# build and start app + postgres together
docker compose -f docker/docker-compose.yml up --build

# stop
docker compose -f docker/docker-compose.yml down
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/logs/ingest` | Ingest and classify a single log |
| `POST` | `/logs/batch` | Ingest and classify multiple logs |
| `GET` | `/logs` | List all classified logs (paginated, filterable) |
| `GET` | `/logs/{id}` | Get a single classified log by ID |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

### Example Request

```bash
curl -X POST http://localhost:8000/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-06-20 10:30:00",
    "source": "BillingSystem",
    "log_message": "Unauthorized access to payment data detected"
  }'
```

### Example Response

```json
{
  "id": 42,
  "timestamp": "2025-06-20 10:30:00",
  "source": "BillingSystem",
  "log_message": "Unauthorized access to payment data detected",
  "predicted_label": "Security Alert",
  "classifier_used": "bert",
  "confidence": 0.9731,
  "severity": "CRITICAL",
  "alert_sent": true,
  "processed_at": "2025-06-20T10:30:01.123456"
}
```

### Filter Logs

```bash
# get only CRITICAL logs
GET /logs?severity=CRITICAL

# get logs from a specific service
GET /logs?source=BillingSystem

# get logs with a specific label
GET /logs?label=Security Alert

# paginate
GET /logs?page=2&size=25
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

```
tests/test_alerts.py::test_critical_error_is_critical      PASSED
tests/test_alerts.py::test_security_alert_is_critical      PASSED
tests/test_classifier.py::test_regex_catches_backup_log    PASSED
tests/test_classifier.py::test_bert_fallback_when_regex_fails PASSED
tests/test_ingest.py::test_health_check                    PASSED
tests/test_ingest.py::test_ingest_single_log               PASSED
...
============= 12 passed in 1.17s =============
```

Tests use **SQLite in-memory** and **mocked ML models** — no PostgreSQL or model downloads needed. This keeps CI fast and dependency-free.

---

## ⚙️ CI/CD Pipeline

Every push to `main` triggers GitHub Actions:

```
Push to GitHub
      ↓
Lint with ruff
      ↓
Run 12 automated tests (SQLite + mocked ML)
      ↓
Build Docker image
      ↓
✅ All green
```

---

## 🏭 Production Architecture Notes

This project is built to simulate a real enterprise AIOps pipeline. In a full production deployment:

| This Project | Production Equivalent |
|---|---|
| `simulate_logs.py` | Filebeat / Fluentd log agents |
| HTTP ingestion | Apache Kafka for high-throughput streaming |
| PostgreSQL | PostgreSQL (structured results) + Elasticsearch (raw log search) |
| Slack webhook | PagerDuty (on-call) + Slack (team notifications) |
| Docker Compose | Kubernetes with horizontal pod autoscaling |
| GitHub Actions | Jenkins / GitLab CI with staging + prod gates |
| Render.com | AWS ECS / EKS |

---

## 📈 Dataset

| Property | Value |
|---|---|
| Total logs | 2,410 |
| Sources | ThirdPartyAPI, ModernHR, BillingSystem, AnalyticsEngine, ModernCRM, LegacyCRM |
| Labels | 9 categories |
| Classifier distribution | Regex: 500 · BERT: 1,903 · LLM: 7 |
| Model accuracy | 100% on synthetic data (~88-92% expected on real-world logs) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| NLP — Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| NLP — Classifier | Scikit-learn Logistic Regression |
| NLP — LLM | Groq API (DeepSeek-R1) |
| Database | PostgreSQL + SQLAlchemy ORM |
| Validation | Pydantic v2 |
| Alerting | Slack Incoming Webhooks |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Linting | Ruff |
| Testing | Pytest + HTTPX |

---

## 🔮 Future Enhancements

- [ ] Elasticsearch integration for raw log full-text search
- [ ] Grafana + Prometheus dashboard for real-time metrics
- [ ] Kafka consumer for high-throughput log streaming
- [ ] Model retraining pipeline with MLflow model registry
- [ ] PagerDuty integration for on-call alerting
- [ ] Kubernetes deployment manifests

---

## 👤 Author

**Your Name**
[GitHub](https://github.com/YOUR_USERNAME) · [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)

---

## 📄 License

MIT License — feel free to use this project as a reference.
