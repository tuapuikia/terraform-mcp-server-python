import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from .config import settings
from loguru import logger

class TFEClient:
    def __init__(self, token: Optional[str] = None, address: Optional[str] = None):
        self.token = token or settings.tfe_token
        self.address = address or settings.tfe_address
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/vnd.api+json"
        } if self.token else {}
        
        self.client = httpx.AsyncClient(
            base_url=self.address.rstrip("/") + "/api/v2",
            headers=headers,
            timeout=30.0,
            verify=not settings.tfe_skip_tls_verify
        )

    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        if not self.token:
            raise ValueError("TFE_TOKEN is required for this operation")
        
        logger.debug(f"Calling TFE: {method} {path}")
        response = await self.client.request(method, path, **kwargs)
        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()

    async def list_organizations(self) -> Dict[str, Any]:
        return await self._request("GET", "/organizations")

    async def list_workspaces(self, org_name: str, **kwargs) -> Dict[str, Any]:
        return await self._request("GET", f"/organizations/{quote(org_name)}/workspaces", params=kwargs)

    async def get_workspace(self, org_name: str, workspace_name: str) -> Dict[str, Any]:
        return await self._request("GET", f"/organizations/{quote(org_name)}/workspaces/{quote(workspace_name)}")

    async def create_workspace(self, org_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", f"/organizations/{quote(org_name)}/workspaces", json={"data": data})

    async def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        return await self._request("DELETE", f"/workspaces/{quote(workspace_id)}")

    async def list_runs(self, workspace_id: str, **kwargs) -> Dict[str, Any]:
        return await self._request("GET", f"/workspaces/{quote(workspace_id)}/runs", params=kwargs)

    async def get_run(self, run_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/runs/{quote(run_id)}")

    async def create_run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/runs", json={"data": data})

    async def close(self):
        await self.client.aclose()

tfe_client = TFEClient()
