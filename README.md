# Terraform MCP Server (Python)

A Python port of the Terraform MCP Server, providing integration with the Terraform Registry and HCP Terraform/TFE.

## Features

- **Dual Transport Support**: Both Stdio and SSE (Streamable HTTP) transports.
- **Terraform Registry Integration**: Public Registry APIs for providers, modules, and policies.
- **HCP Terraform & Terraform Enterprise Support**: Workspace management and run operations.

## Installation

This project is designed to be run with `uv` or `uvx`.

### Using uvx

```bash
uvx --from . terraform-mcp-server stdio
```

### Using uv run

```bash
uv run terraform-mcp-server stdio
```

## Configuration

The server can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TFE_ADDRESS` | HCP Terraform or TFE address | `https://app.terraform.io` |
| `TFE_TOKEN` | Terraform Enterprise API token | None |
| `TFE_SKIP_TLS_VERIFY` | Skip TLS verification | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Available Tools

- `search_providers`: Search for a provider document ID.
- `get_provider_details`: Fetch detailed provider documentation.
- `get_latest_provider_version`: Get latest version of a provider.
- `get_provider_capabilities`: Analyze provider resources and data sources.
- `search_modules`: Search for modules.
- `get_module_details`: Get detailed module information (inputs, outputs).
- `search_policies`: Search for Sentinel/OPA policies.
- `get_policy_details`: Get detailed policy documentation.
- `list_terraform_orgs`: List organizations.
- `list_workspaces`: List workspaces in an organization.
- `get_workspace_details`: Get detailed workspace information.
- `create_workspace`: Create a new workspace.
- `list_runs`: List runs in a workspace.
- `create_run`: Trigger a new run.
- `get_run_details`: Fetch run status and metadata.
