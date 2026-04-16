from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from ..tfe import tfe_client
from loguru import logger
import json

def register_tfe_tools(mcp: FastMCP):
    @mcp.tool()
    async def list_terraform_orgs() -> str:
        """Fetches a list of all Terraform organizations."""
        try:
            data = await tfe_client.list_organizations()
            orgs = data.get("data", [])
            if not orgs:
                return "No organizations found."
            
            results = []
            for org in orgs:
                attrs = org.get("attributes", {})
                results.append(f"- Name: {attrs.get('name')}\n  Email: {attrs.get('email')}")
            
            return "Terraform Organizations:\n\n" + "\n".join(results)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def list_workspaces(terraform_org_name: str) -> str:
        """Search and list Terraform workspaces within a specified organization."""
        try:
            data = await tfe_client.list_workspaces(terraform_org_name)
            workspaces = data.get("data", [])
            if not workspaces:
                return f"No workspaces found in organization {terraform_org_name}."
            
            results = []
            for ws in workspaces:
                attrs = ws.get("attributes", {})
                results.append(f"- ID: {ws['id']}\n  Name: {attrs.get('name')}\n  Execution Mode: {attrs.get('execution-mode')}")
            
            return f"Workspaces in {terraform_org_name}:\n\n" + "\n".join(results)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_workspace(
        terraform_org_name: str,
        workspace_name: str,
        description: str = "",
        terraform_version: str = "",
        execution_mode: str = "remote"
    ) -> str:
        """Creates a new Terraform workspace in the specified organization."""
        try:
            data = {
                "type": "workspaces",
                "attributes": {
                    "name": workspace_name,
                    "description": description,
                    "execution-mode": execution_mode,
                }
            }
            if terraform_version:
                data["attributes"]["terraform-version"] = terraform_version
            
            res = await tfe_client.create_workspace(terraform_org_name, data)
            return f"Workspace created successfully: {res['data']['id']}"
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def delete_workspace_safely(workspace_id: str) -> str:
        """Safely deletes a Terraform workspace by ID. (Ported as basic delete for now)"""
        try:
            await tfe_client.delete_workspace(workspace_id)
            return f"Workspace {workspace_id} deleted successfully."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def list_runs(terraform_org_name: str, workspace_name: str) -> str:
        """List Terraform runs in a specific workspace."""
        try:
            ws = await tfe_client.get_workspace(terraform_org_name, workspace_name)
            ws_id = ws["data"]["id"]
            data = await tfe_client.list_runs(ws_id)
            runs = data.get("data", [])
            if not runs:
                return f"No runs found in workspace {workspace_name}."
            
            results = []
            for run in runs:
                attrs = run.get("attributes", {})
                results.append(f"- ID: {run['id']}\n  Status: {attrs.get('status')}\n  Message: {attrs.get('message')}")
            
            return f"Runs in {workspace_name}:\n\n" + "\n".join(results)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_run(terraform_org_name: str, workspace_name: str, message: str = "Triggered via MCP") -> str:
        """Creates a new Terraform run in the specified workspace."""
        try:
            ws = await tfe_client.get_workspace(terraform_org_name, workspace_name)
            ws_id = ws["data"]["id"]
            data = {
                "type": "runs",
                "attributes": {
                    "message": message,
                },
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": ws_id
                        }
                    }
                }
            }
            res = await tfe_client.create_run(data)
            return f"Run created successfully: {res['data']['id']}"
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_run_details(run_id: str) -> str:
        """Fetches detailed information about a specific Terraform run."""
        try:
            res = await tfe_client.get_run(run_id)
            attrs = res["data"]["attributes"]
            return f"# Run: {run_id}\n- Status: {attrs.get('status')}\n- Message: {attrs.get('message')}\n- Created At: {attrs.get('created-at')}"
        except Exception as e:
            return f"Error: {str(e)}"
