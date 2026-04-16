import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from .config import settings
from loguru import logger

DEFAULT_PUBLIC_REGISTRY_URL = "https://registry.terraform.io"

class RegistryClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=DEFAULT_PUBLIC_REGISTRY_URL,
            timeout=30.0,
            follow_redirects=True,
            verify=not settings.tfe_skip_tls_verify
        )

    async def send_registry_call(self, method: str, uri: str, api_version: str = "v1", params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"/{api_version}/{uri.lstrip('/')}"
        logger.debug(f"Calling Registry: {method} {url}")
        response = await self.client.request(method, url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_latest_provider_version(self, namespace: str, name: str) -> str:
        uri = f"providers/{quote(namespace)}/{quote(name)}"
        data = await self.send_registry_call("GET", uri)
        return data["version"]

    async def get_provider_version_id(self, namespace: str, name: str, version: str) -> str:
        uri = f"providers/{quote(namespace)}/{quote(name)}?include=provider-versions"
        data = await self.send_registry_call("GET", uri, api_version="v2")
        included = data.get("included", [])
        for item in included:
            if item.get("attributes", {}).get("version") == version:
                return item["id"]
        raise ValueError(f"Provider version {version} not found")

    async def get_provider_docs(self, doc_id: str) -> Dict[str, Any]:
        uri = f"provider-docs/{quote(doc_id)}"
        return await self.send_registry_call("GET", uri, api_version="v2")

    async def search_modules(self, query: str, offset: int = 0) -> Dict[str, Any]:
        if query:
            return await self.send_registry_call("GET", "modules/search", params={"q": query, "offset": offset})
        return await self.send_registry_call("GET", "modules", params={"offset": offset})

    async def get_module_details(self, module_id: str) -> Dict[str, Any]:
        uri = f"modules/{quote(module_id)}"
        return await self.send_registry_call("GET", uri)

    async def search_policies(self, query: str) -> Dict[str, Any]:
        uri = "policies?page[size]=100&include=latest-version"
        return await self.send_registry_call("GET", uri, api_version="v2")

    async def get_policy_details(self, policy_id: str) -> Dict[str, Any]:
        uri = f"policies/{quote(policy_id.lstrip('/'))}?include=policies,policy-modules,policy-library"
        return await self.send_registry_call("GET", uri, api_version="v2")

    async def close(self):
        await self.client.aclose()

registry_client = RegistryClient()
