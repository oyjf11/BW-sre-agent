"""API routes package."""
from app.api.incidents import router as incidents_router
from app.api.approvals import router as approvals_router
from app.api.settings import router as settings_router

__all__ = ["incidents_router", "approvals_router", "settings_router"]
