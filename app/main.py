"""

main.py

-------

FastAPI application entry point.
 
- Creates the app instance

- Registers all routers

- Creates DB tables on startup automatically

"""
 
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
 
from app.models.database import engine, Base

from app.routers import ingest, logs

from app.config import settings
 
 
@asynccontextmanager

async def lifespan(app: FastAPI):

    """

    Runs on startup — creates all DB tables if they don't exist.

    SQLAlchemy reads all models that inherit from Base and creates

    their tables automatically. No manual SQL needed.

    """

    print("Starting AIOps Log Classification API...")

    print(f"Environment : {settings.ENVIRONMENT}")

    print("Creating database tables if not exists...")

    Base.metadata.create_all(bind=engine)

    print("Database ready.")

    yield

    print("Shutting down...")
 
 
# ── create FastAPI app ────────────────────────────────────────────────────────

app = FastAPI(

    title       = "AIOps Log Classification API",

    description = """

    Enterprise-grade log classification system using a hybrid NLP approach.
 
    ## How it works

    - **Regex** handles simple, predictable patterns instantly

    - **BERT** (sentence-transformers + Logistic Regression) handles complex logs

    - **LLM** (Groq / DeepSeek) handles LegacyCRM and edge cases
 
    ## Alert System

    - CRITICAL and HIGH severity logs trigger real-time Slack alerts

    - All classified logs are persisted to PostgreSQL

    """,

    version     = "1.0.0",

    lifespan    = lifespan,

)
 
# ── CORS middleware ───────────────────────────────────────────────────────────

# allows browsers / frontend apps to call this API

app.add_middleware(

    CORSMiddleware,

    allow_origins  = ["*"],

    allow_methods  = ["*"],

    allow_headers  = ["*"],

)
 
# ── register routers ──────────────────────────────────────────────────────────

app.include_router(ingest.router)

app.include_router(logs.router)
 
 
@app.get("/", tags=["Root"])

def root():

    return {

        "message"    : "AIOps Log Classification API",

        "version"    : "1.0.0",

        "docs"       : "/docs",

        "health"     : "/health",

        "environment": settings.ENVIRONMENT,

    }
 