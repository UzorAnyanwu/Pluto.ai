from fastapi import APIRouter

from app.api.v1 import ai_agent_config, api_keys, auth, businesses, customers, webhooks

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(auth.router)
api_v1_router.include_router(businesses.router)
api_v1_router.include_router(businesses.team_router)
api_v1_router.include_router(ai_agent_config.router)
api_v1_router.include_router(customers.router)
api_v1_router.include_router(webhooks.router)
api_v1_router.include_router(api_keys.router)
