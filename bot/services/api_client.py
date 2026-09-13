from typing import Any, Dict, List, Optional

import httpx
import structlog

logger = structlog.get_logger()

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("api_request_failed", method=method, endpoint=endpoint, error=str(e))
            return None

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        return await self._request("GET", f"/api/v1/users/telegram/{telegram_id}")

    async def get_grades(self, user_id: str) -> List[Dict[str, Any]]:
        result = await self._request("GET", f"/api/v1/users/{user_id}/grades")
        return result if result else []

    async def get_homework(self, class_id: str) -> List[Dict[str, Any]]:
        result = await self._request("GET", f"/api/v1/classes/{class_id}/homework")
        return result if result else []

    async def get_schedule(self, class_id: str, day: str) -> List[Dict[str, Any]]:
        result = await self._request("GET", f"/api/v1/classes/{class_id}/schedule", params={"day": day})
        return result if result else []

    async def get_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        result = await self._request("GET", f"/api/v1/users/{user_id}/notifications")
        return result if result else []

    async def update_user_language(self, user_id: str, language: str) -> Optional[Dict[str, Any]]:
        return await self._request("PATCH", f"/api/v1/users/{user_id}", json={"language": language})

    async def accept_invite(self, token: str, telegram_id: int, full_name: str) -> Optional[Dict[str, Any]]:
        return await self._request("POST", f"/api/v1/invites/{token}/accept", json={"telegram_id": telegram_id, "full_name": full_name})

    async def close(self):
        await self.client.aclose()

