"""
Grants.gov MCP Server

Provides tools to search federal grant opportunities via the Grants.gov API.
No authentication is required to use this server.
"""

import os

from fastmcp import FastMCP

from grants_gov_mcp.prompts import register_prompts
from grants_gov_mcp.routes import register_routes
from grants_gov_mcp.tools import register_tools

mcp = FastMCP("grants_gov_mcp")

register_routes(mcp)
register_tools(mcp)
register_prompts(mcp)

# Expose ASGI app for uvicorn / cloud deployments
app = mcp.http_app(stateless_http=True)


def main() -> None:
    port_str = os.environ.get("PORT") or os.environ.get("DATABRICKS_APP_PORT")
    if port_str:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=int(port_str))
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
