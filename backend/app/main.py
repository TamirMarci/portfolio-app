from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import holdings, transactions, snapshots, options, prices


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all DB tables on startup (idempotent)
    create_tables()
    yield


app = FastAPI(
    title="Portfolio Tracker API",
    description="Personal investment portfolio tracking backend.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(holdings.router)
app.include_router(transactions.router)
app.include_router(snapshots.router)
app.include_router(options.router)
app.include_router(prices.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
