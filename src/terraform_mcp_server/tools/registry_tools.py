from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from ..registry import registry_client
from ..utils import contains_slug, is_valid_provider_version_format, is_v2_provider_document_type
from loguru import logger

def register_registry_tools(mcp: FastMCP):
    @mcp.tool()
    async def search_providers(
        provider_name: str,
        provider_namespace: str = "hashicorp",
        service_slug: str = "",
        provider_document_type: str = "resources",
        provider_version: str = "latest"
    ) -> str:
        """Search for a provider document ID in the Terraform Registry."""
        try:
            if not provider_version or provider_version == "latest":
                provider_version = await registry_client.get_latest_provider_version(provider_namespace, provider_name)
            
            if is_v2_provider_document_type(provider_document_type):
                # Simplified v2 handling for now
                return f"V2 documentation search for {provider_document_type} not fully implemented in this port yet."

            uri = f"providers/{provider_namespace}/{provider_name}/{provider_version}"
            data = await registry_client.send_registry_call("GET", uri)
            
            docs = data.get("docs", [])
            results = []
            for doc in docs:
                if doc.get("language") == "hcl" and doc.get("category") == provider_document_type:
                    slug = doc.get("slug", "")
                    if service_slug.lower() in slug.lower() or service_slug.lower() in f"{provider_name}_{slug}".lower():
                        results.append(f"- providerDocID: {doc['id']}\n  Title: {doc['title']}\n  Category: {doc['category']}")
            
            if not results:
                return f"No documentation found for service_slug '{service_slug}'"
            
            return "Available Documentation:\n\n" + "\n---\n".join(results)
        except Exception as e:
            logger.error(f"Error searching providers: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_provider_details(provider_doc_id: str) -> str:
        """Fetch detailed Terraform provider documentation using a document ID."""
        try:
            data = await registry_client.get_provider_docs(provider_doc_id)
            return data.get("data", {}).get("attributes", {}).get("content", "No content found")
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_latest_provider_version(namespace: str, name: str) -> str:
        """Fetches the latest version of a Terraform provider from the public registry."""
        try:
            return await registry_client.get_latest_provider_version(namespace, name)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def search_modules(module_query: str, current_offset: int = 0) -> str:
        """Search for Terraform modules in the public registry."""
        try:
            data = await registry_client.search_modules(module_query, current_offset)
            modules = data.get("modules", [])
            if not modules:
                return f"No modules found for query: {module_query}"
            
            results = []
            for m in modules:
                results.append(f"- module_id: {m['id']}\n  Name: {m['name']}\n  Description: {m['description']}\n  Downloads: {m['downloads']}")
            
            return f"Available Terraform Modules for {module_query}:\n\n" + "\n---\n".join(results)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_provider_capabilities(namespace: str, name: str, version: str = "latest") -> str:
        """Get the capabilities of a Terraform provider (resources, data sources, etc.)."""
        try:
            if not version or version == "latest":
                version = await registry_client.get_latest_provider_version(namespace, name)
            
            uri = f"providers/{namespace}/{name}/{version}"
            data = await registry_client.send_registry_call("GET", uri)
            
            docs = data.get("docs", [])
            capabilities = {}
            for doc in docs:
                if doc.get("language") == "hcl":
                    cat = doc.get("category", "other")
                    capabilities[cat] = capabilities.get(cat, 0) + 1
            
            res = f"Provider Capabilities: {namespace}/{name} (v{version})\n\n"
            for cat, count in capabilities.items():
                res += f"- {cat.replace('-', ' ').title()}: {count} available\n"
            
            return res
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def search_policies(policy_query: str) -> str:
        """Search for Terraform policies in the public registry."""
        try:
            data = await registry_client.search_policies(policy_query)
            policies = data.get("data", [])
            results = []
            for p in policies:
                attrs = p.get("attributes", {})
                if policy_query.lower() in attrs.get("title", "").lower() or policy_query.lower() in attrs.get("name", "").lower():
                    # Extract version ID from relationship
                    ver_id = p.get("relationships", {}).get("latest-version", {}).get("links", {}).get("related", "").replace("/v2/", "")
                    results.append(f"- terraform_policy_id: {ver_id}\n  Name: {attrs['name']}\n  Title: {attrs['title']}\n  Downloads: {attrs['downloads']}")
            
            if not results:
                return f"No policies found for query: {policy_query}"
            
            return f"Matching Terraform Policies for {policy_query}:\n\n" + "\n---\n".join(results)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_policy_details(terraform_policy_id: str) -> str:
        """Fetch detailed Terraform policy documentation."""
        try:
            data = await registry_client.get_policy_details(terraform_policy_id)
            attrs = data.get("data", {}).get("attributes", {})
            
            res = f"## Policy details about {terraform_policy_id}\n\n"
            res += attrs.get("readme", "No readme found")
            return res
        except Exception as e:
            return f"Error: {str(e)}"
