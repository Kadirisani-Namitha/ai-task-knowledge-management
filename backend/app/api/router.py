from fastapi import APIRouter

from app.api import auth, health, tasks, documents, search, analytics, users

# We create two aggregators so the endpoints work with or without /api/v1 prefix.
# This ensures E2E test suites or frontends matching either structure succeed.

# 1. Prefixed /api/v1 routes
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(documents.router)
api_router.include_router(search.router)
api_router.include_router(analytics.router)
api_router.include_router(users.router)

# 2. Root routes
root_router = APIRouter()
root_router.include_router(health.router)
root_router.include_router(auth.router)
root_router.include_router(tasks.router)
root_router.include_router(documents.router)
root_router.include_router(search.router)
root_router.include_router(analytics.router)
root_router.include_router(users.router)
